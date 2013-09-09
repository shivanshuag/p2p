import threading
import Queue
import signal
import sys
import sqlite3
import re
from socket import *


def regexp(expr, item):
        reg = re.compile(expr)
        return reg.search(item) is not None

def signal_handler(signal,frame):
        global i
        print "encountered interrupt ctrl+c"
        i=1        

def handle_tasks():
        while 1:
                if not q.empty():
                        task = q.get()
                        print task
                        a = task[1]
                        sock = task[0]
                        job = task[2]
                        if(job[0] == '1'):
                                filelist = job.split('\n')
                                for fil in filelist[1:-1]:
                                        filesplit = fil.split('\t')
                                        print filesplit
                                        filename = filesplit[0]
                                        filepath = filesplit[1]
                                        ip = a[0] + ":" + str(a[1])
                                        cursor.execute('SELECT * FROM files WHERE IP = ? AND Path2file = ?',(a[0] + ":" + str(a[1]),filepath))
                                        if cursor.fetchone() == None :
                                                cursor.execute('INSERT INTO files (IP, Filename, Path2file) values (?, ?, ?)',(ip, filename, filepath))
                                                print "query executed"
                                sock.send("files received")
                        if job[0] == '2':
                                filename = job.split('\n')
                                cursor.execute('SELECT * FROM files WHERE IP != ? AND Filename regexp ?',(a[0] + ":" + str(a[1]),filename[1]))        
                                result = cursor.fetchone()
                                send = ''
                                while result != None:
                                        send+=result[0]+"\t"+result[1]+"\t"+result[2]+"\n"
                                        result = cursor.fetchone()
                                if send=='':
                                        sock.send("no such file")
                                else:
                                        sock.send(send)
                                        



def handle_client(c,a,):
        while 1:
                data = c.recv(1024)
                if len(data)==0:
                        cursor.execute('DELETE FROM files WHERE IP = ?',[a[0] + ":" + str(a[1])])
                        print "connection closed to one client:",a[0]
                        break
                print data
                priority = int(data[0])
                q.put((c,a,data),priority)
        c.close()
        return

i=0
q = Queue.PriorityQueue()
s = socket(AF_INET,SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
conn = sqlite3.connect('p2p.db',check_same_thread = False)
conn.create_function("regexp", 2, regexp)
cursor =conn.cursor()
#cursor.execute('CREATE TABLE IF NOT EXISTS peers(IP TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS files(IP TEXT, Filename TEXT, Path2file TEXT)')
s.bind(("",9006))
s.listen(5)
signal.signal(signal.SIGINT, signal_handler)

taskThread = threading.Thread(target=handle_tasks)
taskThread.daemon = True
taskThread.start()

while True: 
        if i==1:
                print "keyboard interrupt encountered. Closing all connecitons"
                s.close()
                c.close 
                sys.exit(0)
        c,a=s.accept()
        print "Received connection from", a
        #cursor.execute('INSERT INTO peers (IP,) values (?,)',(a,))
        t = threading.Thread(target=handle_client, args=(c,a))
        t.daemon = True
        t.start()