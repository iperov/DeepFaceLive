import multiprocessing
import threading
import time
import traceback
from enum import IntEnum

from ... import db as lib_db
from ...python import Disposable, EventListener

from ..PMPI import PMPI


class Control:
    """
    Base class of control elements between 2 processes.
    """
    class State(IntEnum):
        DISABLED = 0 # the control is not available and unusable (default)
        FREEZED  = 1 # the control is available, but temporary unusable
        ENABLED  = 2 # the control is available and usable


    def __init__(self):
        self._name = None
        self._pmpi = None
        self._pmpi_gather_call_on_msgs = []
        self._pmpi_gather_send_msgs = []
        self._state = Control.State.DISABLED
        self._state_change_evl = EventListener()
        self._call_on_msg('_state', lambda state: self._set_state(state) )

    ##########
    ### PMPI
    def _call_on_msg(self, name, func):
        if self._pmpi is None:
            self._pmpi_gather_call_on_msgs.append( (name,func) )
        else:
            self._pmpi.call_on_msg(f'__{self._name}_{name}__', func)

    def _send_msg(self, name, *args, **kwargs):
        if self._pmpi is None:
            self._pmpi_gather_send_msgs.append( (name,args,kwargs) )
        else:
            self._pmpi.send_msg(f'__{self._name}_{name}__', *args, **kwargs)


    def _set_pmpi(self, pmpi):
        self._pmpi = pmpi
        for name, func in self._pmpi_gather_call_on_msgs:
            self._call_on_msg(name, func)
        self._pmpi_gather_call_on_msgs = []

        for name, args, kwargs in self._pmpi_gather_send_msgs:
            self._send_msg(name, *args, **kwargs)
        self._pmpi_gather_send_msgs = []

    ##########
    ### STATE

    def _set_state(self, state : 'Control.State'):
        if not isinstance(state, Control.State):
            raise ValueError('state must be an instance of Control.State')
        if self._state != state:
            self._state = state
            self._state_change_evl.call(state)
            return True
        return False

    def call_on_change_state(self, func_or_list):
        """Call when the state of the control is changed"""
        self._state_change_evl.add(func_or_list)

    def call_on_control_info(self, func_or_list):
        """Call when the state of the control is changed"""
        self._control_info_evl.add(func_or_list)

    def get_state(self) -> 'Control.State': return self._state
    def is_disabled(self): return self._state == Control.State.DISABLED
    def is_freezed(self): return self._state == Control.State.FREEZED
    def is_enabled(self): return self._state == Control.State.ENABLED


class ControlHost(Control):

    def __init__(self):
        Control.__init__(self)
        self._send_msg('_reset')

    def _set_state(self, state : 'Control.State'):
        result = super()._set_state(state)
        if result:
            self._send_msg('_state', self._state)
        return result

    def disable(self): self._set_state(Control.State.DISABLED)
    def freeze(self):  self._set_state(Control.State.FREEZED)
    def enable(self):  self._set_state(Control.State.ENABLED)

class ControlClient(Control):
    def __init__(self):
        Control.__init__(self)

        self._call_on_msg('_reset', self._reset)

    def _reset(self):
        self._set_state(Control.State.DISABLED)
        self._on_reset()

    def _on_reset(self):
        """Implement when the Control is resetted to initial state,
        the same state like after __init__()
        """
        raise NotImplementedError(f'You should implement {self.__class__} _on_reset')


class SheetBase:
    def __init__(self):
        self._controls = []

    def __setattr__(self, var_name, obj):
        super().__setattr__(var_name, obj)

        if isinstance(obj, Control):
            if obj in self._controls:
                raise ValueError(f'Control with name {var_name} already in Sheet')
            self._controls.append(obj)
            obj._name = var_name

class Sheet:
    """
    base sheet to control CSW
    """
    class Host(SheetBase):
        def __init__(self):
            super().__init__()

    class Worker(SheetBase):
        def __init__(self):
            super().__init__()

class WorkerState:
    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)

class DB(lib_db.KeyValueDB):
    ...

class Base(Disposable):
    """
    base class for Controllable Subprocess Worker (CSW)
    """
    def __init__(self, sheet):
        super().__init__()
        self._pmpi = PMPI()

        if not isinstance(sheet, SheetBase):
            raise ValueError('sheet must be an instance of SheetBase')
        self._sheet = sheet
        for control in sheet._controls:
            control._set_pmpi(self._pmpi)

    def get_control_sheet(self): return self._sheet
    def _get_name(self): return self.__class__.__name__
    def _get_pmpi(self) -> PMPI:  return self._pmpi

class Host(Base):
    """
    Base host class for CSW.


    """

    class _ProcessStatus:
        STOPPING = 0
        STOPPED = 1
        STARTING = 2
        STARTED = 3


    def __init__(self, db : lib_db.KeyValueDB = None,
                       sheet_cls = None,
                       worker_cls = None,
                       worker_state_cls : WorkerState = None,
                       worker_start_args = None,
                       worker_start_kwargs = None,
                       ):
        sheet_host_cls = getattr(sheet_cls, 'Host', None)
        sheet_worker_cls = getattr(sheet_cls, 'Worker', None)

        if sheet_host_cls is None or not issubclass(sheet_host_cls, Sheet.Host):
            raise ValueError('sheet_cls.Host must be an instance Sheet.Host')
        if sheet_worker_cls is None or not issubclass(sheet_worker_cls, Sheet.Worker):
            raise ValueError('sheet_cls.Worker must be an instance Sheet.Worker')
        if not issubclass(worker_cls, Worker):
            raise ValueError("worker_cls must be subclass of Worker")
        if worker_state_cls is None:
            worker_state_cls = WorkerState
        if not issubclass(worker_state_cls, WorkerState):
            raise ValueError("worker_state_cls must be subclass of WorkerState")
        if worker_start_args is None:
            worker_start_args = []
        if worker_start_kwargs is None:
            worker_start_kwargs = {}
        if db is None:
            db = DB()
        if not isinstance(db, DB ):
            raise ValueError("db must be subclass of DB")

        super().__init__(sheet=sheet_host_cls())

        self._worker_cls = worker_cls
        self._worker_sheet_cls = sheet_worker_cls
        self._worker_start_args = worker_start_args
        self._worker_start_kwargs = worker_start_kwargs
        self._worker_state_cls = worker_state_cls
        self._db = db

        self._db_key_host_onoff = f'{self._get_name()}_host_onoff'
        self._db_key_worker_state = f'{self._get_name()}_worker_state'
        state = None
        if db is not None:
            # Try to load the WorkerState
            state = db.get_value (self._db_key_worker_state)
        if state is None:
            # still None - create new
            state = self._worker_state_cls()
        self._state = state

        self._process_status = Host._ProcessStatus.STOPPED
        self._is_busy = False
        self._process = None
        self._reset_restart = False

        self._on_state_change_evl = EventListener()

        self.call_on_msg('_start', self._on_worker_start)
        self.call_on_msg('_stop', self._on_worker_stop )
        self.call_on_msg('_state', self._on_worker_state)
        self.call_on_msg('_busy', self._on_worker_busy)

    def _on_dispose(self):
        self.stop()
        while self._process_status != Host._ProcessStatus.STOPPED:
            self.process_messages()

        super()._on_dispose()

    def call_on_msg(self, name, func): self._pmpi.call_on_msg(name, func)

    def call_on_state_change(self, func_or_list):
        """

            func_or_list    callable(csw, started, starting, stopping, stopped, busy)
        """
        self._on_state_change_evl.add(func_or_list)

    def _on_state_change_evl_call(self):
        self._on_state_change_evl.call(self, self.is_started(), self.is_starting(), self.is_stopping(), self.is_stopped(), self.is_busy() )


    def send_msg(self, name, *args, **kwargs): self._pmpi.send_msg(name, *args, **kwargs)

    def reset_state(self):
        """
        reset state to default
        """
        if self.is_stopped():
            self._state = self._worker_state_cls()
            self._save_state()
        else:
            self._reset_restart = True
            self.stop()

    def save_on_off_state(self):
        """
        save current start/stop state to DB
        """
        if self._process_status == Host._ProcessStatus.STARTED or \
           self._process_status == Host._ProcessStatus.STOPPED:
            # Save only when the process is fully started / stopped
            self._db.set_value(self._db_key_host_onoff, self._process_status == Host._ProcessStatus.STARTED )

    def restore_on_off_state(self, default_state=True):
        """
        restore saved on_off state from db. Default is on.
        """
        is_on = self._db.get_value(self._db_key_host_onoff, default_state)
        if is_on:
            self.start()

    def start(self):
        """
        Start the worker.
        **kwargs will be passed to Worker.on_start(**kwargs)

        returns True if operation is successfully initiated.
        """
        if self._process_status != Host._ProcessStatus.STARTED:

            if self._process_status == Host._ProcessStatus.STOPPED:
                pipe, worker_pipe = multiprocessing.Pipe()
                self._pmpi.set_pipe(pipe)

                self._process_status = Host._ProcessStatus.STARTING
                self._on_state_change_evl_call()

                process = self._process = multiprocessing.Process(target=Worker._start_proc,
                                        args=[self._worker_cls, self._worker_sheet_cls, worker_pipe, self._state, self._worker_start_args, self._worker_start_kwargs],
                                        daemon=True)

                # Start non-blocking in subthread
                threading.Thread(target=lambda: self._process.start(), daemon=True).start()
                time.sleep(0.016) # BUG ? remove will raise ImportError: cannot import name 'Popen' tested in Python 3.6
                return True
        return False

    def stop(self, force=False):
        """
        Stop the module

        arguments:

            force(False)    bool    False: gracefully stop the module(deferred)
                                    True:  force terminate(right now)

        returns True if operation is successfully initiated.

        WARNING !

        Do not kill the process, if it is using any multiprocessing syncronization primivites,
        because if process is killed while any sync is acquired, it will not be released.
        """

        if self._process_status != Host._ProcessStatus.STOPPED:

            if force or self._process_status == Host._ProcessStatus.STARTED:
                if not force:
                    self.send_msg('_stop')
                    self._process_status = Host._ProcessStatus.STOPPING
                    self._on_state_change_evl_call()
                else:
                    self._process.terminate()
                    self._process.join()
                    self._process = None
                    self._pmpi.set_pipe(None)

                    # Reset client controls
                    for control in self.get_control_sheet()._controls:
                        if isinstance(control, ControlClient):
                            control._reset()

                    # Process is physically stopped
                    self._process_status = Host._ProcessStatus.STOPPED
                    self._is_busy = False
                    #print(f'{self._get_name()} is stopped.')
                    self._on_state_change_evl_call()

                return True
        return False

    def is_started(self): return self._process_status == Host._ProcessStatus.STARTED
    def is_starting(self): return self._process_status == Host._ProcessStatus.STARTING
    def is_stopped(self): return self._process_status == Host._ProcessStatus.STOPPED
    def is_stopping(self): return self._process_status == Host._ProcessStatus.STOPPING
    def is_busy(self): return self._is_busy

    def _save_state(self):
        self._db.set_value( self._db_key_worker_state, self._state)

    def _on_worker_start(self):
        self._process_status = Host._ProcessStatus.STARTED
        #print(f'{self._get_name()} is started.')
        self._on_state_change_evl_call()

    def _on_worker_stop(self, error : str = None, restart : bool = False):
        if error is not None:
            print(f'{self._get_name()} error: {error}')
            # Stop on error: reset state
            self._state = self._worker_state_cls()
        self.stop(force=True)

        if self._reset_restart:
            self._reset_restart = False
            self._state = self._worker_state_cls()
            restart = True

        if restart:
            self.start()

    def _on_worker_state(self, state):
        self._state = state
        self._save_state()

    def _on_worker_busy(self, is_busy):
        self._is_busy = is_busy
        self._on_state_change_evl_call()

    def process_messages(self):
        self._pmpi.process_messages()

        if self._process_status == Host._ProcessStatus.STARTED:
            if not self._process.is_alive():
                self.stop(force=True)

class Worker(Base):
    """
    Base Worker class for CSW.
    """

    def __init__(self, sheet):
        super().__init__(sheet=sheet)
        self._started = False
        self._run = True
        self._req_restart = False
        self._req_save_state = False
        self._get_pmpi().call_on_msg('_stop', lambda: setattr(self, '_run', False))

    def on_start(self, *args, **kwargs):
        """overridable"""
    def on_tick(self):
        """
        overridable
        do a sleep inside your implementation
        """

    def on_stop(self):
        """overridable"""

    def send_msg(self, name, *args, **kwargs): self._pmpi.send_msg(name, *args, **kwargs)
    def call_on_msg(self, name, func): self._pmpi.call_on_msg(name, func)
    def restart(self):
        """request to restart Worker"""
        self._req_restart = True
        self._run = False

    def get_state(self) -> WorkerState:
        """
        get WorkerState object of Worker.
        Inner variables can be modified.
        Call save_state to save the WorkerState.
        """
        return self._state

    def save_state(self):
        """Request to save current state"""
        self._req_save_state = True

    def set_busy(self, is_busy : bool):
        """
        indicate to host that worker is in busy mode now
        """
        self.send_msg('_busy', is_busy)

    def is_started(self) -> bool:
        """
        returns True after on_start()
        """
        return self._started

    @staticmethod
    def _start_proc(cls_, sheet_cls, pipe, state, worker_start_args, worker_start_kwargs):
        self = cls_(sheet=sheet_cls())
        self._get_pmpi().set_pipe(pipe)
        self._state = state

        error = None
        try:
            self.on_start(*worker_start_args, **worker_start_kwargs)
            self._started = True
            self.send_msg('_start')
            while True:
                if self._req_save_state:
                    self._req_save_state = False
                    self.send_msg('_state', self._state)

                if not self._run:
                    break

                self._pmpi.process_messages()
                self.on_tick()

            self.on_stop()

        except Exception as e:
            error = f'{str(e)} {traceback.format_exc()}'

        self.send_msg('_stop', error=error, restart=self._req_restart)
        time.sleep(1.0)







