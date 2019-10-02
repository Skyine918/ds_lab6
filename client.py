import ntpath
import os
import socket
import sys
from functools import partial
from threading import Thread


class MainClientThread(Thread):

    def __init__(self, args: dict):
        super().__init__()
        self.host = args["host"]
        self.port = int(args["port"])
        self.filepath = args["filename"]

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            file_size = os.path.getsize("to_send/" + self.filepath)

            with open("to_send/" + self.filepath, "rb") as f:
                s.sendall(MainClientThread.get_filename_from_filepath(self.filepath).encode())
                print(s.recv(512).decode())
                s.sendall(str(file_size).encode())
                print(s.recv(512).decode())
                complete = 0
                print("UPLOAD PERCENTAGE")
                for chunk in iter(partial(f.read, 1024), b''):
                    print((complete / file_size) * 100)
                    s.sendall(chunk)
                    complete += 1024
                if complete >= file_size: print(100, "Complete")

        print("Client thread finished"),

    @staticmethod
    def get_filename_from_filepath(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)


if __name__ == '__main__':
    program_name = sys.argv[0]

    print("Running " + program_name)
    arguments = sys.argv[1:]

    if len(sys.argv) == 4:
        print({"filename": sys.argv[1], "host": sys.argv[2], "port": sys.argv[3]})
        client = MainClientThread({"filename": sys.argv[1], "host": sys.argv[2], "port": sys.argv[3]})
        client.start()
        client.join()
    else:
        print("Wrong number of arguments. ", file=sys.stderr)
