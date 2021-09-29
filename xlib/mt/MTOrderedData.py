from collections import deque
from queue import Queue
from typing import Any, Union, Tuple

def MTOrderedData(queue_size=0):
    """
    Multithreaded ordered work.
    
    Ensures the order of work done by threads.
    returns (host,client)  classes.
    """
    h2c, c2h = Queue(maxsize=queue_size), Queue(maxsize=queue_size)
    
    host = _MTOrderedDataHost(h2c, c2h)
    cli  = _MTOrderedDataClient(h2c, c2h)
    return host, cli

class _MTOrderedDataHost:
    """
    """
    def __init__(self, h2c : Queue, c2h : Queue):
        self._h2c = h2c
        self._c2h = c2h
        self._counter = 0
        
        self._sent_ids = deque()
        self._done_datas = {}
    
    def send(self, data):
        """
        send the data to the clients
        """
        if data is None:
            raise ValueError('data cannot be None')
            
        c = self._counter
        self._counter += 1
        self._sent_ids.append(c)
        
        self._h2c.put( (c, data) )
        
    def recv(self) -> Union[Any, None]:
        sent_ids = self._sent_ids
        
        if len(sent_ids) != 0:
            done_datas = self._done_datas
            
            while not self._c2h.empty():
                id, data = self._c2h.get()
                done_datas[id] = data
            
            id = sent_ids[0]

            if id in done_datas:
                done_data = done_datas.pop(id)
                sent_ids.popleft()
                print('len(sent_ids) ', len(sent_ids))
                return done_data
            
        return None
    
    
class _MTOrderedDataClient:
    
    
    def __init__(self, h2c : Queue, c2h : Queue):
        self._h2c = h2c
        self._c2h = c2h
    
        
    def send(self, data_id, data):
        """
        """
        self._c2h.put( (data_id, data) )
        
        
    def recv(self, wait=True) -> Tuple[int, Any]:
        """
        returns ( data_id(int), data(Any) ) or None
        """
        h2c = self._h2c
        
        if not wait and h2c.empty():
            return None
            
        id, data = h2c.get()
        return id, data
        
    
