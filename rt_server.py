import socket
import threading
import Queue
import sqlite3


def t_func(c,a):
    while 1:
        data = c.recv(10000)
        print data
        if (data.split('\t')[0] == "search"):
        	print "entered search"
        	cur.execute("select * from rttable where filename = ?",[data.split('\t')[1]])
        	print "query executed"
        	res = cur.fetchone()
        	result = ''
        	while res!=None:
        		print "inside loop"
        		result = result + res[0] + "\n"
        		res = cur.fetchone()
        	c.send(result)
        	print result
        if(data.split('\t')[0] == "file"):
        	cur.execute("Insert into rttable values ( ?, ?, ?)",(a[0],data.split('\t')[1],data.split('\t')[2]))		


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

connSql = sqlite3.connect('rt.db',check_same_thread = False)
cur =connSql.cursor()
cur.execute('create table if not exists rttable(peer TEXT, filename TEXT, filepath TEXT)')
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(("",9010))
s.listen(10)
while True: 
        c,a=s.accept()
        thr = threading.Thread(target=t_func, args=(c,a))
        thr.daemon = True
        thr.start()

