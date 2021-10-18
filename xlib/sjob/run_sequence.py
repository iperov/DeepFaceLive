import multiprocessing
from typing import Callable, List

from .. import console as lib_con


def _run_sequence(barrier, init_func, init_kwargs, final_func, process_func, pipe):
    state = {}
    if init_func is not None:
        init_func(state, **init_kwargs)

    barrier.wait()

    while True:
        if pipe.poll(0.05):
            obj = pipe.recv()
            cmd = obj['cmd']
            if cmd == 'job':
                result = process_func(state, obj['data'])
                pipe.send({'cmd':'result', 'data': result})
            elif cmd == 'finalize':
                break

    if final_func is not None:
        final_func(state)

def run_sequence(data_list : List,
                 process_func : Callable,
                 init_func : Callable = None, init_kwargs : dict = None,
                 final_func : Callable = None,
                 mp_count : int = None, progress_bar_desc='Processing'):
    """
    Simple Job to process list of picklable data.

     init_func(state:dict, **init_kwargs)

     process_func(state:dict, data) -> object

     mp_count(None)     number of subprocesses. Default - cores count.
    """
    if mp_count is None:
        mp_count = multiprocessing.cpu_count()

    barrier = multiprocessing.Barrier(mp_count)

    n_data_sent = [0]*mp_count
    conn_list = [None]*mp_count
    p_list = [None]*mp_count

    for i in range(mp_count):
        s_pipe, c_pipe = conn_list[i] = multiprocessing.Pipe()
        p = p_list[i] = multiprocessing.Process(target=_run_sequence, args=(barrier, init_func, init_kwargs, final_func, process_func, c_pipe), daemon=True )
        p.start()

    data_list_len = len(data_list)
    n_data_done = 0
    i_data = 0

    lib_con.progress_bar_print(0, data_list_len, desc=progress_bar_desc)
    result = []
    while n_data_done != data_list_len:

        for n_conn, (s_pipe, _) in enumerate(conn_list):

            if i_data < data_list_len:
                if n_data_sent[n_conn] < 2:
                    n_data_sent[n_conn] += 1

                    data = data_list[i_data]
                    i_data += 1

                    s_pipe.send( {'cmd':'job', 'data':data} )

            if s_pipe.poll(0):
                obj = s_pipe.recv()

                cmd = obj['cmd']
                if cmd == 'result':
                    n_data_done += 1
                    lib_con.progress_bar_print(n_data_done, data_list_len, desc=progress_bar_desc)

                    n_data_sent[n_conn] -= 1

                    data = obj['data']
                    if data is not None:
                        result.append(data)

    for n_conn, (s_pipe, _) in enumerate(conn_list):
        s_pipe.send( {'cmd':'finalize'} )

    return result
