import multiprocessing
import threading
import time
import traceback
import weakref

def _host_thread_proc(wref):
    while True:
        ref = wref()
        if ref is None:
            break
        ref._host_process_messages(0.005)
        del ref
    print('_host_thread_proc exit')

class SPMTWorker:
    def __init__(self, *sub_args, **sub_kwargs):
        """
        base class for single subprocess multi thread worker

        provides messaging interface between host and subprocess
        """
        host_pipe, sub_pipe = multiprocessing.Pipe()
        p = multiprocessing.Process(target=self._subprocess_proc, args=(sub_pipe, sub_args, sub_kwargs), daemon=True)
        p.start()
        self._p = p
        self._pipe = host_pipe

        threading.Thread(target=_host_thread_proc, args=(weakref.ref(self),), daemon=True).start()

    def kill(self):
        """
        kill subprocess
        """
        self._p.terminate()
        self._p.join()

    def stop(self):
        """
        graceful stop subprocess, will wait all thread finalization
        """
        self._send_msg('_stop')
        self._p.join()

    # overridable
    def _on_host_sub_message(self, name, *args, **kwargs):
        """
        a message from subprocess
        """

    def _host_process_messages(self, timeout : float = 0) -> bool:
        """
        process messages on host side
        """
        try:
            pipe = self._pipe
            if pipe.poll(timeout):
                while True:
                    name, args, kwargs = pipe.recv()
                    self._on_host_sub_message(name, *args, **kwargs)
                    if not pipe.poll():
                        break
        except:
            ...

    # overridable
    def _on_sub_host_message(self, name, *args, **kwargs):
        """
        a message from host
        """

    # overridable
    def _on_sub_initialize(self):
        """
        on subprocess initialization
        """

    def _on_sub_finalize(self):
        """
        on graceful subprocess finalization
        """
        print('_on_sub_finalize')

    # overridable
    def _on_sub_thread_initialize(self, thread_id):
        """
        called on subprocess thread initialization
        """
    # overridable
    def _on_sub_thread_finalize(self, thread_id):
        """
        called on subprocess thread finalization
        """
    # overridable
    def _on_sub_thread_tick(self, thread_id):
        """
        called on subprocess thread tick
        """


    def _send_msg(self, name, *args, **kwargs):
        """
        send message to other side (to host or to sub)
        """
        try:
            self._pipe.send( (name, args, kwargs) )
        except:
            ...


    def _sub_thread_proc(self, thread_id):
        self._on_sub_thread_initialize(thread_id)
        while self._threads_running:
            self._on_sub_thread_tick(thread_id)
            time.sleep(0.005)
        self._on_sub_thread_finalize(thread_id)

        self._threads_exit_barrier.wait()

    def _sub_get_thread_count(self) -> int:
        return self._thread_count

    def _subprocess_proc(self, pipe, sub_args, sub_kwargs):
        self._pipe = pipe
        self._thread_count = multiprocessing.cpu_count()

        self._on_sub_initialize(*sub_args, **sub_kwargs)

        self._threads = []
        self._threads_running = True
        self._threads_exit_barrier = threading.Barrier(self._thread_count+1)

        for thread_id in range(self._thread_count):
            t = threading.Thread(target=self._sub_thread_proc, args=(thread_id,), daemon=True)
            t.start()
            self._threads.append(t)

        working = True
        while working:
            if pipe.poll(0.005):
                while True:
                    name, args, kwargs = pipe.recv()
                    if name == '_stop':
                        working = False
                    else:
                        try:
                            self._on_sub_host_message(name, *args, **kwargs)
                        except:
                            print(f'Error during handling host message {name} : {traceback.format_exc()}')

                    if not pipe.poll():
                        break

        self._threads_running = False
        
        self._threads_exit_barrier.wait()

        self._on_sub_finalize()