import multiprocessing
from  multiprocessing.connection import Connection

class PMPI:
    """
    Paired Message Processing Interface

    send and recv messages between processes via pipe
    """
    def __init__(self, pipe : Connection = None):
        self.pipe = pipe
        self.funcs = {}

    def set_pipe(self, pipe):
        self.pipe = pipe

    def call_on_msg(self, name, func):
        """
        Call func on received 'name' message
        """
        if func is None:
            return
        d = self.funcs
        ar = d.get(name, None)
        if ar is None:
            d[name] = ar = []
        ar.append(func)

    def send_msg(self, name, *args, **kwargs):
        """
        send message with name and args/kwargs
        """
        if self.pipe is not None:
            self.pipe.send( (name, args, kwargs) )

    def process_messages(self, timeout=0):
        """
        arguments

         timeout    float sec
        """
        pipe = self.pipe

        try:
            if pipe is not None and pipe.poll(timeout): # poll with timeout only once
                while True:
                    name, args, kwargs = pipe.recv()
                    funcs = self.funcs.get(name, None)
                    if funcs is not None:
                        for func in funcs:
                            func(*args, **kwargs)

                    pipe = self.pipe
                    if pipe is not None and pipe.poll():
                        continue
                    break
        except BrokenPipeError as e:
            self.pipe = None

    # def wait_message(self, name):
    #     """
    #     Wait only specific message and ignore all others.
    #     returns args, kwargs
    #     """
    #     pipe = self.pipe
    #     if pipe is not None:
    #         while True:
    #             if pipe.poll(None):
    #                 msg_name, args, kwargs = pipe.recv()
    #                 if name == msg_name:
    #                     return args, kwargs
    #     return [], {}