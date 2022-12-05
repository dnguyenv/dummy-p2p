# Instruction to run the program 

This README file serves as an instruction for how to run and test the simple peer-to-peer (P2P) system with a centralized index (CI). Here are some highlighted deliverables of this project

 - server processes that wait for connections,
 - client processes that contact a well-known server and exchange data over the network,
 - a simple application protocol and peers and server follow precisely the
specifications for their side of the protocol in order to accomplish particular tasks,
 - a centralized index at the server based on information provided by the peers, and
 - a concurrent server that is capable of carrying out communication with multiple clients 
simultaneously.

# Pre-requisites:

Make sure you have these items addressed before running the program

- Python3 installed
- Ensure the directory named "RFC" is in the same directory as client.
- Ensure this folder exists: `./RFC`
- To run the code, make sure you're in the same dir with this README file

# Run the program

Assuming you're at the root of the project folder (same directory with this README file)

## Running server component:

From one terminal session, run this to start the server

```code
$ python3 server.py
```

You will see some output like this. Depending on what your workstation's domain name is, you will see the `Server name` shows up differently. Record it to use as input for running the peer component

```code
Starting server ...
Server name: D074CWTMVG
```

In the example, `D074CWTMVG` is my server name

## Running client component 

*Note:* Replicate this step to create more client peers as you wish

From another terminal:
```
$ python3 peer.py <ServerPort> <Server name> # This Server name value is from the output of Server component run
```

For example:

```code
$ python3 peer.py 7734 D074CWTMVG
Connected to server at address: D074CWTMVG and port: 7734
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter:
```

Once the Client is up, you can start providing input for service request. Refer to the examples in the next section for more details as for how to run the peer side of the program

## Examples of running the required commands (ADD, GET, LIST, LOOKUP, EXIT)

### ADD command

Client side:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter:
ADD
Enter RFC Number
1
Enter Title
RFC1.txt
ADD request to be sent to the server:
ADD RFC 1  P2P-CI/1.0
Host: 192.168.86.164
Port: 60636
Title: RFC1.txt

ADD response sent from the server:
P2P-CI/1.0 200 OK
Host: 192.168.86.164
Port: 60636
Title: RFC1.txt
```

With that example, you may see something like this on the server side:

```code
Got incoming connection request from  ('192.168.86.164', 60841)
Request received from the client
ADD RFC 1  P2P-CI/1.0
Host: 192.168.86.164
Port: 60636
Title: RFC1.txt
```

### GET command:

If the system found the information requested, you will see something like this

From Client side:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
GET
Enter RFC Number
1
Enter Title
RFC1.txt
LOOKUP Request to be sent to the server for completing the GET request
LOOKUP RFC 1 P2P-CI/1.0
Host: 192.168.86.164
Port: 60636
Title: RFC1.txt

LOOKUP Response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 192.168.86.164 60636

GET request to be sent to the peer holding the RFC file
GET RFC 1 P2P-CI/1.0
Host: 192.168.86.164
OS: macOS-12.6-arm64-arm-64bit

Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
Connection with peer established
GET message response:
P2P-CI/1.0 200 OK
Date: Mon, 05 Dec 2022 04:07:20 GMT
OS: macOS-12.6-arm64-arm-64bit
Last-Modified: Tue Nov 22 20:09:25 2022
Content-Length: 21082
Content-Type: text/plain

Network Working Group                                   Steve Crocker
Request for Comments: 1                                          UCLA
                                                         7 April 1969


                         Title:   Host Software
                        Author:   Steve Crocker
                          Installation:   UCLA
                          Date:   7 April 1969
             Network Working Group Request for Comment:   1
........ more data here .........

File Received from peer and stored locally now
```

If there is no info found, you will see something like this

```code
$ python3 peer.py 7734 D074CWTMVG
Connected to server at address: D074CWTMVG and port: 7734
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
GET
Enter RFC Number
10
Enter Title
RFC10.txt
LOOKUP Request to be sent to the server for completing the GET request
LOOKUP RFC 10 P2P-CI/1.0
Host: 192.168.86.164
Port: 60092
Title: RFC10.txt

LOOKUP Response sent from the server
P2P-CI/1.0 404 Not Found

```

### LIST command

On the client/peer side:

```code
$ python3 peer.py 7734 D074CWTMVG
Connected to server at address: D074CWTMVG and port: 7734
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LIST
LIST request to be sent to the server
LIST ALL P2P-CI/1.0
Host: 192.168.86.164
Port: 60209

LIST Response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 192.168.86.164 60636
RFC 2 RFC2.txt 192.168.86.164 60092
RFC 3 RFC3.txt 192.168.86.164 60092

Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter:
```

In the response details, you may notice that there are 3 records listed. The first RFC 1 belongs to the peer `192.168.86.164:60636`, the last 2 items belong to `192.168.86.164:60092`

On server side, you may see something like this 

```code
Request received from the client
LIST ALL P2P-CI/1.0
Host: 192.168.86.164
Port: 60209
```

### LOOKUP command

On any client/peer terminal, you can perform this LOOKUP command. Here is an example

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LOOKUP
Enter RFC Number
4
Enter Title
RFC4.txt
LOOKUP request to be sent to the server
LOOKUP RFC 4 P2P-CI/1.0
Host: 192.168.86.164
Port: 60209
Title: RFC4.txt

Retrieving response sent from the server
P2P-CI/1.0 200 OK
RFC 4 RFC4.txt 192.168.86.164 60209

Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 

```

On server side, you may see this output

```code
Request received from the client
LOOKUP RFC 4 P2P-CI/1.0
Host: 192.168.86.164
Port: 60209
Title: RFC4.txt
```

### EXIT command

This command is issued from one of the active peers. From a arbitrary active peer terminal, issue a `LIST` command first to list all the peers in the system to verify:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LIST
LIST request to be sent to the server
LIST ALL P2P-CI/1.0
Host: 192.168.86.164
Port: 60092

LIST Response sent from the server
P2P-CI/1.0 200 OK
RFC 1 RFC1.txt 192.168.86.164 60636
RFC 2 RFC2.txt 192.168.86.164 60092
RFC 3 RFC3.txt 192.168.86.164 60092
RFC 4 RFC4.txt 192.168.86.164 60209

Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter:
```

We see that there currently are 3 active peers in the system. Now issue an EXIT command from a peer:

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
EXIT
```

and check the LIST command again from 1 of remaining peers, the resources associated with the EXITed peer should be removed out of the list. In this example, the record belongs to `192.168.86.164:60636` has been removed as the EXIT command was issued from `192.168.86.164:60636` peer's terminal

```code
Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: 
LIST
LIST request to be sent to the server
LIST ALL P2P-CI/1.0
Host: 192.168.86.164
Port: 60092

LIST Response sent from the server
P2P-CI/1.0 200 OK
RFC 2 RFC2.txt 192.168.86.164 60092
RFC 3 RFC3.txt 192.168.86.164 60092
RFC 4 RFC4.txt 192.168.86.164 60209

```

## Tips for NCSU server setup 

### Enable a to be accessible from outside

TCP

```code
$ sudo iptables -I INPUT -p tcp -s 0.0.0.0/0 --dport 7734 -j ACCEPT
$ sudo ufw allow 7734 
$ sudo ufw reload
```

or UDP

```code
$ sudo iptables -I INPUT -p udp -s 0.0.0.0/0 --dport 7734 -j ACCEPT
$ sudo ufw allow 7734 
$ sudo ufw reload
```