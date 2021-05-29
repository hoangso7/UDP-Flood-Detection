import socket


flag = b'ptitctf{network-monitoring-udp-flood-detection-is-cool}\n'
tryagain = b'you foo. try again plz\n'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 31337

server = (server_address, server_port)
sock.bind(server)
print("Listening on " + server_address + ":"+str(server_port))

while True:
	payload, client_address = sock.recvfrom(1024)

	
	recv = payload.decode('utf-16')
	recv = recv[:-1]

	print ("Receive: \'" + recv + "\' from "+str(client_address))

	if (recv == 'gimme ur flag!'):
		sent = sock.sendto(flag, client_address)
	else:
		sent = sock.sendto(tryagain, client_address)
