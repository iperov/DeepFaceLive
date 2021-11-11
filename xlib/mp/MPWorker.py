import multiprocessing
import threading
import time
import traceback
import weakref
from typing import List

class MPWorker:
    def __init__(self, sub_args : List = None,
                       process_count : int = None ):
        """
        base class for multi process worker

        provides messaging interface between host and subprocesses


         sub_args   a list of args will be passed to _on_sub_initialize

         process_count  number of subprocesses. Default : number of cpu count

        starts immediatelly after construction.
        """
        if process_count is None:
            process_count = multiprocessing.cpu_count()

        pipes = []
        ps = []
        for i in range(process_count):
            host_pipe, sub_pipe = multiprocessing.Pipe()

            p = multiprocessing.Process(target=self._sub_process, args=(i, process_count, sub_pipe, sub_args), daemon=True)
            p.start()

            pipes += [host_pipe]
            ps += [p]

        self._process_id = -1
        self._process_count = process_count
        self._process_working_count = process_count
        self._pipes = pipes
        self._ps = ps

        threading.Thread(target=_host_thread_proc, args=(weakref.ref(self),), daemon=True).start()

    # overridable
    def _on_host_sub_message(self, process_id, name, *args, **kwargs):
        """a message from subprocess"""
    # overridable
    def _on_sub_host_message(self, name, *args, **kwargs):
        """a message from host"""
    # overridable
    def _on_sub_initialize(self, *args):
        """on subprocess initialization"""
    # overridable
    def _on_sub_finalize(self):
        """on graceful subprocess finalization"""
    # overridable
    def _on_sub_tick(self, process_id):
        """"""
    def get_process_count(self) -> int: return self._process_count
    def get_process_id(self) -> int: return self._process_id

    def kill(self):
        """
        kill subprocess
        """
        for p in self._ps:
            p.kill()
        self._ps = []

    def stop(self):
        """
        graceful stop subprocess, will wait all subprocess finalization
        """
        self._send_msg('__stop')
        for p in self._ps:
            p.join()
        self._ps = []

    def _host_process_messages(self, timeout : float = 0) -> bool:
        """
        process messages on host side
        """
        for process_id, pipe in enumerate(self._pipes):
            try:
                if pipe.poll(timeout):
                    name, args, kwargs = pipe.recv()
                    if name == '__stopped':
                        self._process_working_count -= 1
                    else:
                        self._on_host_sub_message(process_id, name, *args, **kwargs)
            except:
                ...

    def _send_msg(self, name, *args, process_id=-1, **kwargs):
        """
        send message to other side

         process_id     -1 mean send to all sub processes
                        on subprocess side - ignore this param
        """
        try:
            for i, pipe in enumerate(self._pipes):
                if process_id == -1 or i == process_id:
                    pipe.send( (name, args, kwargs) )
        except:
            ...

    def _sub_process(self, process_id, process_count, pipe, sub_args):
        self._process_id = process_id
        self._process_count = process_count
        self._pipes = [pipe]

        self._on_sub_initialize(*sub_args)

        working = True
        while working:
            self._on_sub_tick(process_id)

            if pipe.poll(0.005):
                while True:
                    name, args, kwargs = pipe.recv()
                    if name == '__stop':
                        working = False
                    else:
                        try:
                            self._on_sub_host_message(name, *args, **kwargs)
                        except:
                            print(f'Error during handling host message {name} : {traceback.format_exc()}')

                    if not pipe.poll():
                        break

        self._on_sub_finalize()

def _host_thread_proc(wref):
    while True:
        ref = wref()
        if ref is None:
            break
        ref._host_process_messages(0)
        del ref
        time.sleep(0.005)