import glob
import os
import socket
import sys
from threading import Thread


class ConnectionThread(Thread):
    def __init__(self, args: dict):
        super().__init__()
        self.conn = args["conn"]
        self.addr = args["addr"]

    def run(self):

        conn = self.conn
        addr = self.addr
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        with conn:
            print('Connected by', addr)
            filename = conn.recv(512).decode()
            conn.sendall(b"NAME RECEIVED")
            filesize = int(conn.recv(512).decode())
            conn.sendall(b"LENGTH RECEIVED")
            print("FILENAME RECEIVED ON SERVER: " + filename)
            print("FILESIZE RECEIVED ON SERVER: " + str(filesize))

            filename = self.resolve_collision_and_get_name(filename, os.path.splitext(filename)[1])

            f = open("" + filename, "wb")
            data = conn.recv(1024)
            while data:
                f.write(data)
                data = conn.recv(1024)

    @classmethod
    def resolve_collision_and_get_name(cls, filename, extension, num=1):
        files = glob.glob("./*" + extension)
        flag = 0
        for file in files:
            name = file[2:]
            if name == filename:
                flag = 1
                break
        if flag == 1:
            if num == 1:
                filename = filename[:(len(filename) - len(extension))]
                filename = filename + '_copy' + str(num) + extension
                return cls.resolve_collision_and_get_name(filename, extension, num + 1)
            else:
                filename = filename[:(len(filename) - len(extension) - 5 - len(str(num - 1)))]
                filename = filename + '_copy' + str(num) + extension
                return cls.resolve_collision_and_get_name(filename, extension, num + 1)
        else:
            return filename


class MainServerThread(Thread):

    def __init__(self, args: dict):
        super().__init__()

        self.port = int(args["port"])

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.bind(('', self.port))
            s.listen()
            while True:
                print("--------------------------------------")
                conn, addr = s.accept()
                client_thread = ConnectionThread({"conn": conn, "addr": addr})
                client_thread.start()

                # with conn:
                #
                #     print('Connected by', addr)
                #     filename = conn.recv(512).decode()
                #     filesize = int(conn.recv(512).decode())
                #     print("FILENAME RECEIVED ON SERVER: " + filename)
                #     print("FILESIZE RECEIVED ON SERVER: " + str(filesize))
                #     f = open("to_receive/" + filename, "wb")
                #     data = conn.recv(1024)
                #     while data:
                #         f.write(data)
                #         data = conn.recv(1024)

        print("Server thread finished"),


if __name__ == '__main__':
    program_name = sys.argv[0]

    print("Running Server", program_name)
    arguments = sys.argv[1:]

    if len(sys.argv) == 2:
        print({"port": sys.argv[1]})
        client = MainServerThread({"port": sys.argv[1]})
        client.start()
        client.join()
    else:
        print("Wrong number of arguments. ", file=sys.stderr)
