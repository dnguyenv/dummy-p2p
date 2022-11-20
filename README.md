# Instruction to run the program 

## Pre-requisites:

- Python3 installed
- Ensure the directory named "RFC" is in the same directory as client.
- This entry is in `/etc/hosts` file: `127.0.0.1 localhost` (MacOS)
- This folder exists: `./RFC`
- To run the code, make sure you're in the same dir with this README file

## Running server component:

From one terminal session:
```code
$ python3 server.py
```

Example output:

```code
The server is ready and up
Server name: 127.0.0.1
```

In the example, `127.0.0.1` is the server name, record it to use as input for running the peer component

## Running client component 

*Note:* Replicate this step to create more client peers 

From another terminal:
```
$ python3 peer.py <ServerPort> <Server name> # This Server name value is from the output of Server component run
```
Example:

```code
$ python3 peer.py 7734 localhost
Connected to server at address: localhost and port: 7734
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
```

Once Client is up, please provide input for service request.

## Examplle:

### ADD:

Client side:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter:
ADD
Enter RFC Number
1
Enter Title
RFC1.txt
ADD Request to be sent to the server
ADD RFC 1 P2P-CI/1.0
Host: 127.0.0.1
Port: 60671
Title: RFC1.txt
```

Server side output:

```code
Got incoming connection request from  ('127.0.0.1', 55004)
Request received from the client
ADD RFC 1 P2P-CI/1.0
Host: 127.0.0.1
Port: 60972
Title: RFC1.txt
```


### GET:

If info found:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
GET
Enter RFC Number
1
Enter Title
RFC1.txt
LOOKUP Request to be sent to the server for completing the GET request
LOOKUP RFC 1 P2P-CI/1.0
Host: 127.0.0.1
Port: 60824
Title: RFC1.txt

LOOKUP Response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 127.0.0.1 60824

GET request to be sent to the peer holding the RFC file
GET RFC 1 P2P-CI/1.0
Host: 127.0.0.1
OS: macOS-12.6-arm64-arm-64bit

Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
Connection with peer established
GET message response:
P2P-CI/1.0 200 OK
Date: Sun, 20 Nov 2022 20:39:58 GMT
OS: macOS-12.6-arm64-arm-64bit
Last-Modified: Sun Nov 20 13:41:09 2022
Content-Length: 21082
Content-Type: text/plain

Network Working Group                                   Steve Crocker
Request for Comments: 1                                          UCLA
                                                         7 April 1969
........ more data here .........

File Received from peer and stored locally now
```

If there is no info found:
```code
$ python3 peer.py 7734 localhost
Connected to server at address: localhost and port: 7734
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter:
GET
Enter RFC Number
1
Enter Title
RFC1.txt
LOOKUP Request to be sent to the server for completing the GET request
LOOKUP RFC 1 P2P-CI/1.0
Host: 127.0.0.1
Port: 60848
Title: RFC1.txt

LOOKUP Response sent from the server
P2P-CI/1.0 404 Not Found

```

### LIST

peer side:

```code
$ python3 peer.py 7734 localhost
Connected to server at address: localhost and port: 7734
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LIST
LIST request to be sent to the server
LIST ALL P2P-CI/1.0
Host: 127.0.0.1
Port: 60953

LIST Response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 127.0.0.1 60824
RFC 3 RFC3.txt 127.0.0.1 60300
RFC 13 RFC13.txt 127.0.0.1 60953

Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter:
```

Server side:

```code
Request received from the client
LIST ALL P2P-CI/1.0
Host: 127.0.0.1
Port: 60887
```

### LOOKUP

Client side:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LOOKUP
Enter RFC Number
1
Enter Title
RFC1.txt
LOOKUP request to be sent to the server
LOOKUP RFC 1 P2P-CI/1.0
Host: 127.0.0.1
Port: 60953
Title: RFC1.txt

Retrieving response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 127.0.0.1 60824

```

Server side:

```code
Request received from the client
LOOKUP RFC 1 P2P-CI/1.0
Host: 127.0.0.1
Port: 60953
Title: RFC1.txt
```

### EXIT

This command is issued from one of the active peers. From a random peer, issue a `LIST` command first to list all the peers in the system to verify:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LIST
LIST request to be sent to the server
LIST ALL P2P-CI/1.0
Host: 127.0.0.1
Port: 60824

LIST Response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 127.0.0.1 60824
RFC 3 RFC3.txt 127.0.0.1 60300
RFC 13 RFC13.txt 127.0.0.1 60953
```

We see that there currently are 3 active peers in the system. Now issue an EXIT command for a peer:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
EXIT
```

and check the LIST command again from 1 of remaining peers, the resources associated with the EXITed peer should be removed out of the list

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LIST
LIST request to be sent to the server
LIST ALL P2P-CI/1.0
Host: 127.0.0.1
Port: 60953

LIST Response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 127.0.0.1 60824
RFC 13 RFC13.txt 127.0.0.1 60953

```