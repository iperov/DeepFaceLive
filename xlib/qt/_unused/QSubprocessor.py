import multiprocessing
import sys
import time
import traceback

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from .qtex import *

class QSubprocessor(object):
    """
    
    """

    class Cli(object):
        def __init__ ( self, client_dict ):
            s2c = multiprocessing.Queue()
            c2s = multiprocessing.Queue()
            self.p = multiprocessing.Process(target=self._subprocess_run, args=(client_dict,s2c,c2s) )
            self.s2c = s2c
            self.c2s = c2s
            self.p.daemon = True
            self.p.start()

            self.state = None
            self.sent_time = None
            self.sent_data = None
            self.name = None
            self.host_dict = None

        def kill(self):
            self.p.terminate()
            self.p.join()

        #overridable optional
        def on_initialize(self, client_dict):
            #initialize your subprocess here using client_dict
            pass

        #overridable optional
        def on_finalize(self):
            #finalize your subprocess here
            pass

        #overridable
        def process_data(self, data):
            #process 'data' given from host and return result
            raise NotImplementedError

        #overridable optional
        def get_data_name (self, data):
            #return string identificator of your 'data'
            return "undefined"

        def log_info(self, msg): self.c2s.put ( {'op': 'log_info', 'msg':msg } )
        def log_err(self, msg):  self.c2s.put ( {'op': 'log_err' , 'msg':msg } )
        def progress_bar_inc(self, c): self.c2s.put ( {'op': 'progress_bar_inc' , 'c':c } )

        def _subprocess_run(self, client_dict, s2c, c2s):
            self.c2s = c2s
            data = None
            try:
                self.on_initialize(client_dict)
                c2s.put ( {'op': 'init_ok'} )
                while True:
                    msg = s2c.get()
                    op = msg.get('op','')
                    if op == 'data':
                        data = msg['data']
                        result = self.process_data (data)
                        c2s.put ( {'op': 'success', 'data' : data, 'result' : result} )
                        data = None
                    elif op == 'close':
                        break
                    time.sleep(0.001)
                self.on_finalize()
                c2s.put ( {'op': 'finalized'} )
            except Exception as e:
                c2s.put ( {'op': 'error', 'data' : data} )
                if data is not None:
                    print ('Exception while process data [%s]: %s' % (self.get_data_name(data), traceback.format_exc()) )
                else:
                    print ('Exception: %s' % (traceback.format_exc()) )
            c2s.close()
            s2c.close()
            self.c2s = None

        # disable pickling
        def __getstate__(self):
            return dict()
        def __setstate__(self, d):
            self.__dict__.update(d)

    #overridable
    def __init__(self, name, SubprocessorCli_class, no_response_time_sec = 0, io_loop_sleep_time=0.005):
        if not issubclass(SubprocessorCli_class, QSubprocessor.Cli):
            raise ValueError("SubprocessorCli_class must be subclass of QSubprocessor.Cli")

        self.name = name
        self.SubprocessorCli_class = SubprocessorCli_class
        self.no_response_time_sec = no_response_time_sec
        self.io_loop_sleep_time = io_loop_sleep_time

        self.clis = []

        #getting info about name of subprocesses, host and client dicts, and spawning them
        for name, host_dict, client_dict in self.process_info_generator():
            try:
                cli = self.SubprocessorCli_class(client_dict)
                cli.state = 1
                cli.sent_time = 0
                cli.sent_data = None
                cli.name = name
                cli.host_dict = host_dict

                self.clis.append (cli)
            except:
                raise Exception (f"Unable to start subprocess {name}. Error: {traceback.format_exc()}")

        if len(self.clis) == 0:
            raise Exception ("Unable to start QSubprocessor '%s' " % (self.name))

        #waiting subprocesses their success(or not) initialization
        while True:
            for cli in self.clis[:]:
                while not cli.c2s.empty():
                    obj = cli.c2s.get()
                    op = obj.get('op','')
                    if op == 'init_ok':
                        cli.state = 0
                    elif op == 'log_info':
                        print(obj['msg'])
                    elif op == 'log_err':
                        print(obj['msg'])
                    elif op == 'error':
                        cli.kill()
                        self.clis.remove(cli)
                        break
            if all ([cli.state == 0 for cli in self.clis]):
                break
            time.sleep(0.005)

        if len(self.clis) == 0:
            raise Exception ( "Unable to start subprocesses." )

        #ok some processes survived, initialize host logic
        self.on_clients_initialized()
                
        self.q_timer = QTimer()
        self.q_timer.timeout.connect(self.tick)
        self.q_timer.start(5)
        
    #overridable
    def process_info_generator(self):
        #yield per process (name, host_dict, client_dict)
        for i in range(min(multiprocessing.cpu_count(), 8) ):
            yield 'CPU%d' % (i), {}, {}

    #overridable optional
    def on_clients_initialized(self):
        #logic when all subprocesses initialized and ready
        pass

    #overridable optional
    def on_clients_finalized(self):
        #logic when all subprocess finalized
        pass

    #overridable
    def get_data(self, host_dict):
        #return data for processing here
        raise NotImplementedError

    #overridable
    def on_data_return (self, host_dict, data):
        #you have to place returned 'data' back to your queue
        raise NotImplementedError

    #overridable
    def on_result (self, host_dict, data, result):
        #your logic what to do with 'result' of 'data'
        raise NotImplementedError

    def tick(self):
        for cli in self.clis[:]:
            while not cli.c2s.empty():
                obj = cli.c2s.get()
                op = obj.get('op','')
                if op == 'success':
                    #success processed data, return data and result to on_result
                    self.on_result (cli.host_dict, obj['data'], obj['result'])
                    self.sent_data = None
                    cli.state = 0
                elif op == 'error':
                    #some error occured while process data, returning chunk to on_data_return
                    if 'data' in obj.keys():
                        self.on_data_return (cli.host_dict, obj['data'] )
                    #and killing process
                    cli.kill()
                    self.clis.remove(cli)
                elif op == 'log_info':
                    print(obj['msg'])
                elif op == 'log_err':
                    print(obj['msg'])
                elif op == 'progress_bar_inc':
                    ...
                    #io.progress_bar_inc(obj['c'])

        for cli in self.clis[:]:
            if cli.state == 1:
                if cli.sent_time != 0 and self.no_response_time_sec != 0 and (time.time() - cli.sent_time) > self.no_response_time_sec:
                    #subprocess busy too long
                    print ( '%s doesnt response, terminating it.' % (cli.name) )
                    self.on_data_return (cli.host_dict, cli.sent_data )
                    cli.kill()
                    self.clis.remove(cli)

        for cli in self.clis[:]:
            if cli.state == 0:
                #free state of subprocess, get some data from get_data
                data = self.get_data(cli.host_dict)
                if data is not None:
                    #and send it to subprocess
                    cli.s2c.put ( {'op': 'data', 'data' : data} )
                    cli.sent_time = time.time()
                    cli.sent_data = data
                    cli.state = 1

        if all ([cli.state == 0 for cli in self.clis]):
            #gracefully terminating subprocesses
            for cli in self.clis[:]:
                cli.s2c.put ( {'op': 'close'} )
                cli.sent_time = time.time()

            while True:
                for cli in self.clis[:]:
                    terminate_it = False
                    while not cli.c2s.empty():
                        obj = cli.c2s.get()
                        obj_op = obj['op']
                        if obj_op == 'finalized':
                            terminate_it = True
                            break

                    if (time.time() - cli.sent_time) > 30:
                        terminate_it = True

                    if terminate_it:
                        cli.state = 2
                        cli.kill()

                if all ([cli.state == 2 for cli in self.clis]):
                    break

            #finalizing host logic
            self.q_timer.stop()
            self.q_timer = None
            self.on_clients_finalized()
            
