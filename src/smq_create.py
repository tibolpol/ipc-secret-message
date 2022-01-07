#!/usr/bin/env python3
"""
Create a new private System-V IPC queue.
Return key + id

The IPC object should be available only to the creating
process or its child processes (e.g. those created with fork()).
"""

from __future__ import  print_function
from  sys       import  stderr, stdout
from  sysv_ipc  import  MessageQueue, Semaphore, IPC_CREX

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

# create queue and semaphore
queue = MessageQueue(None,IPC_CREX)
sema1 = Semaphore(queue.key,IPC_CREX,initial_value = 1)
sema2 = Semaphore(queue.key+1,IPC_CREX,initial_value = 1)
print(str(queue.key) + " " + str(queue.id) + " " + str(sema1.id) + " " + str(sema2.id))
