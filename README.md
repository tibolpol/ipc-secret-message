# ipc-secret-message
Python implementation of send/receive a secret message via IPC queue. In this implementation, the receiver process can read the complete message only if child of a trusted process.

Use Case : 3 roles involved.
- OWNER the owner of data
- PROXY the owner of proxy
- USER the user of data

OWNER delegates to PROXY to give to USER the access to data. PROXY runs the service, OWNER shares the data through the service with a private key, but does not want PROXY to be able to use this key out of the service.
With this implementation of IPC queue, OWNER can guarantee that only trusted children process of the service can read the key, PROXY cannot steal the OWNER's key.

This implementation suits well with a socat listener and few lines of bash scripts.

<pre>
read IPC_QUEUE IPC_QUEUEID IPC_SEM1ID IPC_SEM2ID < <( smq_create.py )
socat UNIX-LISTEN:proxy,fork,mode=777 EXEC:"smq_receive.py $IPC_QUEUE "<( #subprocess IPC send
  while smq_send.py $IPC_QUEUE socat <<< "$(mcrypt -q -k XYZ <<< "$MESSAGE" | base64 -w0)" ; do : ; done
    ipcrm -q $IPC_QUEUEID -s $IPC_SEM1ID -s $IPC_SEM2ID
  ),stderr &</pre>

The activation process tree will look like this :
<pre>
socat UNIX-LISTEN:proxy,fork,mode=777 EXEC:smq_receive queue_id /dev/fd/62,stderr
 \_ smq_send queue_id socat
 \_ smq_receive queue_id /dev/fd/62</pre>

No other processes other than the ones forked by socat can read the message, because smq_send verifies the reader parents PPID before delivering the complete message. Stealing peaces to the raw IPC queue is possible but never get the complete message, and a partial message won't be decrypted. The message will be very hard to steal even for root.
