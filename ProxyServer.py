import socket
import sys

def main():
    if len(sys.argv) <= 1:
        print("Usage: python ProxyServer.py server_ip")
        sys.exit(2)

    # Create a server socket, bind it to a port, and start listening
    tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSerPort = 8888
    tcpSerSock.bind(('127.0.0.1', tcpSerPort))
    tcpSerSock.listen(1)

    while True:
        print("Ready to serve...")
        tcpCliSock, addr = tcpSerSock.accept()
        print("Received a connection from:", addr)

        message = tcpCliSock.recv(1024).decode()
        if not message:
            continue

        if "GET /www.google.com" not in message:
            continue

        if "GET /favicon.ico" in message:
            continue

        print(message)

        filename = message.split()[1].partition("/")[2]
        print(filename)

        fileExist = False
        filetouse = "/" + filename
        print(filetouse)

        try:
            # Check whether the file exists in the cache
            f = open(filetouse[1:], "r")
            outputdata = f.read()
            fileExist = True

            # ProxyServer finds a cache hit and generates a response message
            response = "HTTP/1.0 200 OK\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += outputdata

            tcpCliSock.send(response.encode())
            tcpCliSock.close()
            f.close()
            print("Read from cache")
        except IOError:
            if not fileExist:
                # Create a socket on the proxy server
                c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                hostn = filename.replace("www.", "", 1)
                print(hostn)

                try:
                    # Connect to the socket to port 80
                    c.connect((hostn, 80))
                    print("Socket connected to port 80 of the host")

                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobj = c.makefile('r', 0)
                    request = "GET http://" + filename + " HTTP/1.0\r\n\r\n"
                    c.send(request.encode())

                    response = ""
                    while True:
                        data = c.recv(1024)
                        if not data:
                            break
                        response += data

                    # Create a new file in the cache for the requested file
                    tmpFile = open("./" + filename, "wb")
                    tmpFile.write(response)
                    tmpFile.close()

                    tcpCliSock.send(response)
                except:
                    print("Illegal request")
            else:
                # HTTP response message for file not found
                status_line = 'HTTP/1.1 404 Not Found\r\n\r\n'
                tcpCliSock.send(status_line.encode())

            tcpCliSock.close()

    tcpSerSock.close()

if __name__ == "__main__":
    main()
