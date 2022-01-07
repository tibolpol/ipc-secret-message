#!/usr/bin/env python3
"""
Send a message on a secure System-V IPC queue.

- argv  : queue, master_name
- read msg
- slice msg into msg1+msg2
- send msg1 to queue
- expect msg1 from queue
- check legal pid and echo
- send msg2 to queue

This script is supposed to speak to smq_receive.py
Both processes must be children of the same process of name master_name.
"""

from __future__ import  print_function
from  sys       import  argv, stderr
from  sysv_ipc  import  MessageQueue, Semaphore
from  psutil    import  Process
from  os        import  getpid
import psutil

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

# slice msg
msg = input()
msg1= msg[0:int(len(msg)/2)]
msg2= msg[int(len(msg)/2):len(msg)]

# args
queue = MessageQueue(int(argv[1]))
master_name = argv[2]

# master process must be the nearest parent with the exact given name
master_proc = Process(getpid())
while master_proc.name() != master_name :
  master_proc = master_proc.parent()

with Semaphore(int(argv[1])) :
  try :
    # send-receive echo
    # type=1 : from me to other
    # type=2 : to me from other
    queue.send(msg1,type=1)
    # will block until a process claims the rest of the message
    (echo1, echo_type) = queue.receive(type=2)
    echo_proc = Process(queue.last_send_pid)
  
    if echo1.decode("ascii") == msg1 :
      parent = echo_proc 
      try :
        while parent.pid != master_proc.pid :
          parent = parent.parent()
      except :
        pass
  
      # finish the message
      if parent :
        queue.send(msg2,type=1)
  
      # refuse to speak if no common ancestor process
      else :
        eprint("refused " + format(echo_proc) + " from " + echo_proc.username())
        # clear
        try :
          while True :
            queue.receive(block=False)
        except :
          pass
  
    # refuse to speak to wrong echo
    else :
      eprint("received " + echo1.decode("ascii") + " sent " + msg1 + " from " + format(echo_proc) + " from " + echo_proc.username())
      # clear
      try :
        while True :
          queue.receive(block=False)
      except :
        pass
  
  except :
    raise
