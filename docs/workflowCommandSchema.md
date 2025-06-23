# Run Workflow Commands

## Command: PING 

### Description
The `PING` command will prompt the workflow to verify that it is running. The workflow will just respond with the text "PONG". 

### Syntax

```
PING
```

### Notes
- The server will respond with the message "PONG"

## Command: STOP 

### Description
The `STOP` command will end the running clip creation workflow. This stops clip creation, but will not immediately kill the program. Moreover, any clips that are in the process of being recorded or saved will finish being proccessed. In addition, 

### Syntax

```
STOP
```

### Notes
- If a clip is being recored, clip creation will end after recording is done 
- All clips in the post clip handling queue will be handled 

## Command: KILL 

### Description
The `KILL` command will forecfully terminate the clip creation workflow and will stop all processes.

### Syntax

```
KILL
```

### Notes
- If a clip is being recorded, recording will stop and the clip will be discarded
- All clips in the post recording queue will not be handled
- Clips in the middle of being uploaded will probably fail 
