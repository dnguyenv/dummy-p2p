""" 
Authors Stephen Bennett & Duy Ngyuen
November 15, 2022
"""

import socket, random, platform, time
import pickle as pickle
from _thread import *

"""Starting the TCP server socket """
server_port = 7734
#serverName = socket.gethostbyname('localhost') # Lets use localhost for simplicity
server_name = socket.gethostname() # Lets use localhost for simplicity
#serverName = serverName + '.local' # If running on Mac Big Sur or later, un comment this one
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((server_name,server_port))
serverSocket.listen(5)

print('Starting server ...')
print('Server name: ' + server_name)

"""Initialize the structures for peer data """

# key: ip_value 
# value: upload_port_number
peer_info_dict={}

# key: rfc_number 
# value: list of host_names (ips)
peer_rfc_dict={}

# key: rfc_number 
# value: rfc_title
rfc_number_title_dict={}

""" Adding the intial client upload port data into the data structure """
def insert_data_in_dict(initial_data,hostname):
	global peer_info_dict
	peer_info_dict[hostname] = initial_data[0]

""" Adding the RFC to the data structures """
def add_peer_rfc(rfc_number,rfc_title,client_host_name):
	global peer_rfc_dict,rfc_number_title_dict
	if not (rfc_number in rfc_number_title_dict):
		rfc_number_title_dict[rfc_number] = rfc_title
		peer_rfc_dict[rfc_number ] = [client_host_name]
	else:
		rfc_host_list = peer_rfc_dict.get(rfc_number)
		rfc_host_list.append(client_host_name)
		peer_rfc_dict[rfc_number] = rfc_host_list

"""Looking up the RFC and forms the response having the information of the peers holding it"""
def lookup_peer(rfc_number,rfc_title,client_host_name,client_port_number):
	global peer_rfc_dict,rfc_number_title_dict

	if rfc_number in rfc_number_title_dict and rfc_number_title_dict.get(rfc_number) == rfc_title:
		message = 'P2P-CI/1.0 200 OK'
		rfc_host_list = peer_rfc_dict.get(rfc_number)
		for host in rfc_host_list:
			temp = f'RFC {rfc_number} {rfc_title} {host[:host.find(":")]} {peer_info_dict.get(host)}'
			message = message + '\r\n' + temp
		message += '\r\n'
	else:
		message = 'P2P-CI/1.0 404 Not Found\r\n'
	return message

"""Building a list of all the RFCs and the response with the info of the peers holding it"""
def list_peer(client_host_name):
	global peer_rfc_dict,rfc_number_title_dict
	rfc_list = peer_rfc_dict.keys()
	if len(rfc_list) == 0:
		message = 'P2P-CI/1.0 404 Not Found\r\n'
	else:
		message = 'P2P-CI/1.0 200 OK'
		for rfc in rfc_list:
			rfc_host_list = peer_rfc_dict.get(rfc)
			for host in rfc_host_list:
				temp = f'RFC {rfc} {rfc_number_title_dict.get(rfc)} {host[:host.find(":")]} {peer_info_dict.get(host)}'
				message = message + '\r\n' + temp
		message += '\r\n'
	return message

"""The server thread that handles all the requests for ADD, LOOKUP, LIST and EXIT"""
def client_init(connectionsocket, addr):
	
	"""Retrieving the initial data sent by client, including its upload port number"""
	initial_data = pickle.loads(connectionsocket.recv(1024))
	host_name = f'{addr[0]}:{initial_data[0]}'

	"""Adding the information into the data structures"""
	insert_data_in_dict(initial_data,host_name)

	while True:
		"""Request received from client for a service """
		message_received = connectionsocket.recv(1024)
		message_list = pickle.loads(message_received)

		print('Request received from the client')
		print(message_list[0])

		"""EXIT request"""
		if message_list[0][0] == 'E': # pretty dumb inspection
			break

		# ADD request
		elif message_list[0][0] == 'A':			
			split_data = message_list[0].split('\r\n')
			"""Checking for BAD REQUEST case"""
			
			if len(split_data)==5 and "ADD RFC " in split_data[0] and "Host: " in split_data[1] and "Port: " in split_data[2] and "Title: " in split_data[3]:
				"""Checking for VERSION NOT SUPPORTED case
				If the request is OK then add the data from the request and echo back the same request with OK response"""
				if 'P2P-CI/1.0' in split_data[0]:
					message_head = split_data[0].split(' ') # extract the message head
					"""Retrieving the newly added RFC file information from request"""
					rfc_number = message_head[2].strip()
					client_host_name = split_data[1].split(' ')[1].strip()
					client_port_number = split_data[2].split(' ')[1].strip()
					rfc_title = split_data[3].split(' ')[1].strip()

					p2p_version = message_head[3].strip()	
					

					"""Adding the RFC file info into the data structures """
					add_peer_rfc(rfc_number,rfc_title,client_host_name + ":" + client_port_number)
					
					"""Sending back OK response to the client"""
					message = f'P2P-CI/1.0 200 OK\r\n{split_data[1]}\r\n{split_data[2]}\r\n{split_data[3]}\r\n'
					connectionsocket.send(message.encode())
				else:
					message = '505 P2P-CI Version Not Supported\r\n'
					connectionsocket.send(message.encode())
			else:
				message = '400 Bad Request\r\n'
				connectionsocket.send(message.encode())

		#LIST Request
		elif message_list[0][0] == 'L':
			if message_list[0][1] == 'I':
				split_data = message_list[0].split('\r\n')
				"""Checking for BAD REQUEST case """
				if len(split_data) == 4 and 'LIST ALL ' in split_data[0] and 'Host: ' in split_data[1] and 'Port: ' in split_data[2]:
					message_head = split_data[0].split(' ') # extract the message head
					p2p_version = message_head[2].strip()	

					"""Checking for VERSION NOT SUPPORTED case
					If it's ok then respond with the list of RFCs and their peer info"""
					if p2p_version == 'P2P-CI/1.0':
						"""Retrieving information from request"""
						client_host_name = split_data[1].split(' ')[1].strip()
						client_port_number = split_data[2].split(' ')[1].strip()
						"""Sending the response to client """
						message = list_peer(f'{client_host_name}:{client_port_number}')
						connectionsocket.send(message.encode())
					else:
						message='505 P2P-CI Version Not Supported\r\n'
						connectionsocket.send(message.encode())
				else:
					message='400 Bad Request\r\n'
					connectionsocket.send(message.encode())

			#LOOKUP Request
			else:
				split_data = message_list[0].split('\r\n')				
				"""Checking for BAD REQUEST case """
				if len(split_data) == 5 and 'LOOKUP RFC ' in split_data[0] and 'Host: ' in split_data[1] and 'Port: ' in split_data[2] and 'Title: ' in split_data[3]:
					message_head = split_data[0].split(' ') # extract the message head

					p2p_version = message_head[3].strip()
					"""Checking for VERSION NOT SUPPORTED case
					If it's ok then respond with the requested RFC file info """
					if p2p_version == 'P2P-CI/1.0':
						"""Retrieving requested RFC file information from request"""						
						rfc_number = message_head[2].strip()
						client_host_name = split_data[1].split(' ')[1].strip()
						client_port_number = split_data[2].split(' ')[1].strip()
						rfc_title = split_data[3].split(' ')[1].strip()
						"""Respond to the request by sending the RFC file information to client"""
						message = lookup_peer(rfc_number,rfc_title,client_host_name + ":" + client_port_number,client_port_number)
						connectionsocket.send(message.encode())
					else:
						message='505 P2P-CI Version Not Supported\r\n'
						connectionsocket.send(message.encode())
				else:
					message='400 Bad Request\r\n'
					connectionsocket.send(message.encode())
	
	"""If the client EXITS, remove all the information for that client from the data structures"""
	print(f'Client existing ...')
	if host_name in peer_info_dict:
		peer_info_dict.pop(host_name,None)
	rfc_list = peer_rfc_dict.copy().keys()
	for rfc in rfc_list:
		rfc_host_list=peer_rfc_dict.get(rfc)
		if host_name in rfc_host_list:
			if len(rfc_host_list)==1:
				rfc_number_title_dict.pop(rfc,None)
				peer_rfc_dict.pop(rfc,None)
			else:
				rfc_host_list.remove(host_name)
				peer_rfc_dict[rfc]=rfc_host_list
	"""Close the connection thread for that client"""
	connectionsocket.close()

"""Keep the server socket alive"""
while True:
	"""Accept incoming connection request from client"""
	connectionsocket, addr = serverSocket.accept()
	print('Got incoming connection request from ', addr)
	"""Thread handles incoming requests from clients and respond back to them """
	start_new_thread(client_init, (connectionsocket, addr))

serverSocket.close()