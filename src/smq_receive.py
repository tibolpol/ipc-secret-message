#!/usr/bin/env python
"""
Receive a message on a secure System-V IPC queue.

- argv : queue
- receive msg1
- echo    msg1
- receive msg2
- return  msg1 + msg2

This script is supposed to speak to smq_send.py
Both processes must be children of the same process.
"""

from __future__ import  print_function
from  sys       import  argv, stderr
from  sysv_ipc  import  MessageQueue, BusyError, Semaphore

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

with Semaphore(int(argv[1])+1) :
  queue = MessageQueue(int(argv[1]))
  try :
    
    # type=1 : to me from other
    # type=2 : from me to other
    (msg1, type) = queue.receive(type=1)
  
    queue.send(msg1,type=2)
    (msg2, type) = queue.receive(type=1)
    print(msg1 + msg2)
  except BusyError :
    queue.send("fake",block=False,type=2)
    raise
