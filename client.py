# TODO status line

from socket import *
from Tkinter import *
import tkFileDialog
import tkMessageBox
import threading
CONNECT = 0

s = socket(AF_INET,SOCK_STREAM)
root = Tk()
def close():
        s.close()
        root.quit()

root.protocol("WM_DELETE_WINDOW", close)

Label(root, text="IP").grid(row=0)
E1 = Entry(root)
E1.grid(row=0,column=1)
E1.focus_set()

Label(root, text="Port").grid(row=1)
E2 = Entry(root)
E2.grid(row=1,column=1)
def connect():
    ip = E1.get()
    port = int(E2.get())
    try:
    	global CONNECT
    	a = s.connect((ip,port))
    	print a
    	CONNECT = 1
    	print CONNECT
    	t = threading.Thread(target=peer_server)
    	t.daemon = True
    	t.start()

    except Exception,e:
        tkMessageBox.showwarning(
            "Connect",
            "Something\'s wrong with %s:%d. Exception type is %s" % (ip, port, `e`)
        )
        return
    print "connected"    	
    #status.set("connected")

buttonConnect = Button(root, text="connect", width=10, command=connect)
buttonConnect.grid(row=2,column=1)

Label(root, text="Share Files:").grid(row=3)
fileEntry = StringVar()
EFiles = Entry(root, textvariable=fileEntry)
EFiles.grid(row=3,column=1)
fileEntry.set("")
filez = ()
def browse():
	global filez
	filez = tkFileDialog.askopenfilenames(parent=root,title='Choose a file')
	entry = ''
	for fil in filez:
		entry =entry+fil+", "
	fileEntry.set(entry)

buttonBrowse = Button(root, text="Browse", width=5, command=browse)
buttonBrowse.grid(row=3,column=2)
def share():
	send = ""
	#print filez
	for fil in filez:
		replaced = fil.replace ("\t", "\\\t")
		#print "replaced spaces"
		listPath = fil.split("/")
		fileName = listPath[len(listPath)-1]
		#print fileName
		send+=(fileName+"\t"+replaced+"\n")
	send = "1\n" + send
	print send
	if CONNECT==1:
		try:
			s.send(send)
			data = s.recv(1000)
			print data
			#TODO receive the data and display to user
		except Exception,e:
			tkMessageBox.showwarning(
	            "Search",
	            "Something\'s wrong . Exception type is %s" %`e`
	        )
			return
		print "Sending Query"    
	else:
		tkMessageBox.showwarning(
			"Not Connected",
			"Please connect to a server first"
		)
	#TODO send and receive data
buttonShare = Button(root, text="Share", width=10, command=share)
buttonShare.grid(row=4,column=1)

Label(root, text="Search Files:").grid(row=5)
entrySearch = Entry(root)
entrySearch.grid(row=5,column=1)

def download(listbox):
	fil =  listbox.get(listbox.curselection())
	fillist = fil.split("      ")
	peer = fillist[0].split(":")
	peerIp = peer[0]
	peerPort = int(peer[1]) + 1
	filename = fillist[1].split("/")[len(fillist[1].split("/")) - 1]
	d = socket(AF_INET,SOCK_STREAM)
	try:
		d.connect((peerIp,peerPort))
		print "connected to peer"
		d.send(fillist[1])
		f = open(filename+"_"+peerIp+"Dwonload", 'wb')
		l = d.recv(1024)
		while l:   
			f.write(l)
			l = d.recv(1024)
		f.close()
	except Exception,e:
		tkMessageBox.showwarning(
            "Search",
            "Something\'s wrong. Exception type is %s" % `e`
        )
		return



def search():
	query = "2\n"+entrySearch.get()
	if CONNECT==1:
		try:
			s.send(query)
			data = s.recv(1000)
			print data
			if(data != "no such file"):
				listbox = Listbox(root, width=50)
				listbox.grid(row=6,columnspan=4)
				filelist = data.split('\n')
				for fil in filelist[:-1]:
					fillist = fil.split('\t')
					print fillist
					peer = fillist[0]
					path = fillist[2]
					listbox.insert(END, peer+'      '+path)
				buttonDownload = Button(root, text="Download", width=5, command=lambda: download(listbox))
				buttonDownload.grid(row=7,column=1)
			else:
				tkMessageBox.showwarning(
	            	"Search",
	            	"No such file by other peers"
	        	)		
		except Exception,e:
			tkMessageBox.showwarning(
	            "Search",
	            "Something\'s wrong. Exception type is %s" % `e`
	        )
			return

		#print "Sending Query"    
	else:
		tkMessageBox.showwarning(
			"Not Connected",
			"Please connect to a server first"
		)	
	#TODO send search query	
buttonSearch = Button(root, text="Search", width=5, command=search)
buttonSearch.grid(row=5,column=2)

def disconnect():
	global s
	s.close()
	s = socket(AF_INET,SOCK_STREAM)

buttonDisconnect = Button(root, text="Disconnect", width=10, command=disconnect)
buttonDisconnect.grid(row=8,column=1)

def handle_client(c,a):
	print "inside thread"
	path2file = c.recv(1024)
	print path2file
	try:
		f=open(path2file, "rb")
		l = f.read(1024)
		while len(l):
			c.send(l)
			l=f.read(1024)
			print "sent 1024 bytes"
		print "EOF"	
		f.close()	
		c.close()	
	except Exception,e:	
		tkMessageBox.showwarning(
        "Search",
        "Something\'s wrong. Exception type is %s" % `e`
    )
	return

def peer_server():
	print "peer server started"
	p = socket(AF_INET,SOCK_STREAM)
	p.bind(("",s.getsockname()[1]+1))
	p.listen(5)
	while True: 
		c,a=p.accept()
		print "received connection from ",a[0]
		thr = threading.Thread(target=handle_client, args=(c,a))
		print "1"
		thr.daemon = True
		print "2"
		thr.start()
		print "3"
		

root.mainloop()