""" 
Authors Stephen Bennett & Duy Ngyuen
November 15, 2022
"""

import socket
import os
import pickle as pickle
import random
from _thread import *
import platform
import time
import email.utils
import sys

""" Getting server Information: Server IP address, port from command line """
serverPort = int(sys.argv[1])
serverName = sys.argv[2]

""" This is to store the RFCs that the client currently has at the starting time """
client_RFC_list = {}	

""" Connect to the server socket via TCP """
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
print(f'Connected to server at address: {serverName} and port: {serverPort}')
client_hostname=clientSocket.getsockname()[0]

"""Building ADD request message"""
def create_add_request(client_rfc_num,client_rfc_title):
	message = f'ADD RFC {client_rfc_num}  P2P-CI/1.0\r\n'
	message += f'Host: {client_hostname}\r\n'
	message += f'Port: {upload_client_port_number}\r\n'
	message += f'Title: {client_rfc_title}\r\n'
	return message

"""Building the GET request message """
def create_get_request(client_rfc_num):
	message = f'GET RFC {client_rfc_num} P2P-CI/1.0\r\n'
	message += f'Host: {client_hostname}\r\n'
	message += f'OS: {platform.platform()}\r\n'
	return message

"""Building the LOOKUP request message"""
def create_lookup_request(client_rfc_num, client_rfc_title):
	message = f'LOOKUP RFC {client_rfc_num} P2P-CI/1.0\r\n'
	message += f'Host: {client_hostname}\r\n'
	message += f'Port: {upload_client_port_number}\r\n'
	message += f'Title: {client_rfc_title}\r\n'
	return message

"""Building the LIST request message"""
def create_list_request():
	message = f'LIST ALL P2P-CI/1.0\r\n'
	message += f'Host: {client_hostname}\r\n'
	message += f'Port: {upload_client_port_number}\r\n'
	return message

"""
Upload server socket which is always listening for incoming file upload requests from other peers
If the requests are sent properly then it responds with the desired RFC file data
"""
def upload_thread():
	
	"""Creating an upload server socket"""
	uploadSocket = socket.socket()
	host='0.0.0.0' # Accept from all interfaces
	uploadSocket.bind((host,upload_client_port_number))
	uploadSocket.listen(5)
	while True:
		"""Accept an incoming request for upload"""
		downloadSocket,downloadAddress = uploadSocket.accept()
		message = downloadSocket.recv(1024).decode() # Need to decode the content
		split_data = message.split('\r\n')
		
		""" Inspect for BAD REQUEST case """
		if len(split_data) == 4 and "GET RFC" in split_data[0] and "Host: " in split_data[1] and "OS: " in split_data[2]:
			"""Inspect for VERSION NOT SUPPORTED case """
			if 'P2P-CI/1.0' in split_data[0]:
				
				request=split_data[0].split(' ')
				if request[0]=='GET':

					# Extract the request RFC number from the input
					rfc_number=request[2]

					# Locate the file and retrieve data

					rfc_file_path = f'{os.getcwd()}/RFC/RFC{rfc_number}.txt'
					
					opened_file = open(rfc_file_path,'r')
					data = opened_file.read()

					"""Building the response to the requesting peer """

					reply_message = f'P2P-CI/1.0 200 OK\r\n'
					reply_message += f'Date: {email.utils.formatdate(usegmt=True)}\r\n'
					reply_message += f'OS: {platform.platform()}\r\n'
					reply_message += f'Last-Modified: {time.ctime(os.path.getmtime(rfc_file_path))}\r\n'
					reply_message += f'Content-Length: {len(data)}\r\n'
					reply_message += f'Content-Type: text/plain\r\n'
					reply_message = reply_message + data
					
					print(f'GET message response:')
					print(f'{reply_message}')

					# Respond back
					downloadSocket.sendall(reply_message.encode()) 
			else:
				reply_message = f'505 P2P-CI Version Not Supported\r\n'
				downloadSocket.send(reply_message.encode())
		else:
			reply_message = f'400 Bad Request\r\n'
			downloadSocket.send(reply_message.encode())

""" This function handles GET request and receiving the RFC file from it"""
def download_rfc_thread(req_message,peer_host_name,peer_port_number,rfc_number):

	"""Connecting to the uploading server socket of the peer holding the desired file """
	requestPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	requestPeerSocket.connect((peer_host_name,int(peer_port_number)))
	
	print ('Connection with peer established')

	"""Sending GET request to the peer """
	requestPeerSocket.sendall(req_message.encode())
	
	"""Retriving the response from the peer """
	get_reply = ''
	get_reply = requestPeerSocket.recv(1024).decode()

	if 'P2P-CI/1.0 200 OK' in get_reply.split('\r\n')[0]:
		print ('P2P-CI/1.0 200 OK')
		content_line = (get_reply.split('\r\n'))[4]
		content_length = int(content_line[content_line.find('Content-Length: ')+16:])
		get_reply = get_reply + requestPeerSocket.recv(content_length).decode()
		rfc_file_path = f'{os.getcwd()}/RFC/RFC{rfc_number}.txt'
		data = get_reply[get_reply.find('text/plain\r\n') + 12 :]

		"""Writing the data to a file """
		with open(rfc_file_path,'w') as file:
			file.write(data)
		print ('File Received from the peer and stored locally now')

	elif 'Version Not Supported' in get_reply.split("\r\n")[0]: # dump inspection 
		print (get_reply)
	elif 'Bad Request' in get_reply.split("\r\n")[0]:
		print (get_reply)

	"""Closing the socket connection """
	requestPeerSocket.close()

""" This function handles GET, ADD, LOOKUP, LIST and EXIT commands"""
def user_input():

	print ('Type your desired command (ADD, GET, LIST, LOOKUP or EXIT) and hit Enter: ')

	service = input()

	if service == 'ADD':

		print ('Enter RFC Number')
		client_rfc_num = input()
		print ('Enter Title')
		client_rfc_title = input()

		rfc_file_path = f'{os.getcwd()}/RFC/RFC{client_rfc_num}.txt'

		if os.path.isfile(rfc_file_path):
						
			req_message = create_add_request(client_rfc_num,client_rfc_title)

			print('ADD request to be sent to the server:')
			print(req_message)

			information_list = [req_message]
			info_add = pickle.dumps(information_list,-1)
			clientSocket.send(info_add)
			
			""" Getting the response from server and print it out """
			response_received = clientSocket.recv(1024).decode()
			print('ADD response sent from the server:')
			print(response_received)
		else:
			print('The file is not found')

		user_input()

	elif service == 'GET':

		print ('Enter RFC Number')
		client_rfc_num = input()
		print ('Enter Title')
		client_rfc_title = input()

		""" Creating a LOOKUP request to find the peer holding the requesting RFC. Send it to the server """
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)

		print ('LOOKUP Request to be sent to the server for completing the GET request')
		print (req_message)

		information_list = [req_message]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.sendall(info_add)

		"""Retrieving response to LOOKUP from the server"""
		response_received = clientSocket.recv(1024).decode()

		"""Based on the server response, inspect the response for FILE NOT FOUND, BAD REQUEST or WRONG VERSION ... """
		split_data=response_received.split('\r\n')

		print ('LOOKUP Response sent from the server')
		
		""" ... by a very dumb check for now, as long as it does the job ... """
		if '404 Not Found' in split_data[0]:
			print (response_received)
		elif 'Version Not Supported' in split_data[0]:
			print (response_received)
		elif 'Bad Request' in split_data[0]:
			print (response_received)
		else:
			print (response_received)

			"""
			Retrieve the Hostname(IP) and Port number of the first peer in the response holding the RFC file 
			Note: Actually this should be the last one instead, which would cover the case where new peer ADDs same 
			content ... To be revisited
			"""
			split_data=split_data[1].split(' ')
			peer_host_name=split_data[3]
			peer_port_number=split_data[4]

			"""Building the GET request to be sent to the peer"""
			req_message = create_get_request(client_rfc_num)
			
			print ('GET request to be sent to the peer holding the RFC file')
			print (req_message)

			"""Start a new thread that handles sending the GET request and retrieving the RFC file"""
			start_new_thread(download_rfc_thread,(req_message,peer_host_name,peer_port_number,client_rfc_num))

		user_input() 

	elif service == 'LIST':

		"""Building the LIST request to be sent to the server"""
		req_message = create_list_request()

		print ('LIST request to be sent to the server')
		print (req_message)

		"""Sending the List request to the server"""
		information_list = [req_message]
		info_add = pickle.dumps(information_list,-1)
		clientSocket.send(info_add)

		"""Retrieving the response from the server"""
		response_received = clientSocket.recv(1024).decode()

		print ('LIST Response sent from the server')
		print (response_received)

		user_input()

	elif service == 'LOOKUP':

		print ('Enter RFC Number')
		client_rfc_num = input()
		print ('Enter Title')
		client_rfc_title = input()

		"""Buildiing a LOOKUP request to be sent to the server"""
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)

		print ('LOOKUP request to be sent to the server')
		print (req_message)

		"""Sending the request to the server"""
		information_list = [req_message]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.send(info_add)

		"""Retrieving the response from the server"""
		response_received = clientSocket.recv(1024).decode()

		print('Retrieving response sent from the server')
		print (response_received)

		user_input()

	elif service == 'EXIT':
		"""This part handles the case when the user wants to stop the client by sending EXIT command
		The information will be relayed to the server
		The server will then remove information related to all the files that this client had
		The client socket connection to the server will be closed """
		message = 'EXIT'
		exit_message = pickle.dumps([message],-1)		
		clientSocket.send(exit_message)
		clientSocket.close()
	else:
		print ('Wrong input. Please try again.')
		user_input()

"""
Retrieving the initial peer file data from the directory and 
sending ADD requests to server for each of them
"""
def send_peer_info(clientSocket):
	rfc_numbers=[]
	rfc_titles=[]
	rfc_storage_path = f'{os.getcwd()}/RFC'
	for file_name in os.listdir(rfc_storage_path):
		if 'RFC' in file_name:
			rfc_number = file_name[file_name.find('C') + 1 : file_name.find('.')]
			rfc_title = file_name
			"""Create and send an ADD request for each file"""
			req_message = create_add_request(rfc_number,rfc_title)
			print ('ADD Request to be sent to the server')
			print (req_message)
			information_list = [req_message]
			info_add = pickle.dumps(information_list,-1)
			clientSocket.send(info_add)
			"""Retrieving the response from server then print it"""
			response_received = clientSocket.recv(1024).decode()
			print ('ADD Response sent from the server')
			print (response_received)

"""Generating the random client port number it will use for uploading """
upload_client_port_number = 60000 + random.randint(1,1000)

"""Sending the upload port information to the server"""
data = pickle.dumps([upload_client_port_number])
clientSocket.send(data)
clientSocket.close

"""This is for quick testing ... generating the initial peer file data and send it to the server"""
#send_peer_info(clientSocket)

"""Starts a new thread that handles the upload server socket over the random upload port generated"""
start_new_thread(upload_thread,())
""" This is the entry point, the function that handles GET, ADD, LOOKUP, LIST and EXIT request"""
user_input()

