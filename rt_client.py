import socket
import threading

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("127.0.0.1",9010))
while 1:
	inp = raw_input("Give 1 to share file and 2 to search file")
	if(inp == '1'):
		filename = raw_input("Give the filename")
		filepath = raw_input("Give the filepath")
		s.send("file\t"+filename+"\t"+filepath)
	elif(inp == '2'):
		query = raw_input("Give the filename to search")
		s.send("search\t"+query)
		data = s.recv(1000)
		peerlist = data.split('\n')
		for peer in peerlist:
			print "Peer"+peer+"has this file"
	else:
		print "wrong input"		
