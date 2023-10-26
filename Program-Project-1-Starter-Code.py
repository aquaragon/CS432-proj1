import socket
import os

def main():
    # Create a server socket
    server_ip = '127.0.0.1'  # Replace with your server IP
    server_port = 8888

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)

    print(f"Proxy server is listening on {server_ip}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()

        # Receive the client's request
        request = client_socket.recv(1024).decode()

        # Extract the URL from the request
        url = request.split(' ')[1]

        # Check if the requested URL is in the cache
        if os.path.exists(url):
            with open(url, 'rb') as cache_file:
                response = cache_file.read()
            print(f"Sending cached content for {url}")
        else:
            # If not in cache, forward the request to the remote server
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((url, 80))
            remote_socket.send(request.encode())

            # Receive the response from the remote server
            response = remote_socket.recv(4096)

            # Cache the response
            with open(url, 'wb') as cache_file:
                cache_file.write(response)

        # Send the response to the client
        client_socket.send(response)
        client_socket.close()

if __name__ == "__main__":
    main()
