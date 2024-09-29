import socket
import threading
import logging
from file_utils import chunk_file
logging.basicConfig(level=logging.INFO)

# Function to handle incoming client requests
def handle_client(client_socket, file_chunks):
    try:
        # Receive the request from the client (up to 1024 bytes)
        request = client_socket.recv(1024).decode('utf-8')  # Decode the received bytes into a string

        # If the request starts with "GET_CHUNK", process the chunk request
        if request.startswith("GET_CHUNK"):
            # Extract the chunk index from the request (assuming it's formatted as "GET_CHUNK <chunk_index>")
            chunk_index = int(request.split()[1])  # Split the request and get the second part as the chunk index
            
            # Check if the requested chunk index is valid (i.e., within the bounds of the available chunks)
            if 0 <= chunk_index < len(file_chunks):
                logging.info(f"Serving chunk {chunk_index} to client.")
                # Send the requested chunk back to the client
                client_socket.sendall(file_chunks[chunk_index])
            else:
                # If the chunk index is invalid, send an empty response
                client_socket.sendall(b'')
    except Exception as e:
        logging.error(f"Error handling client request: {e}")
        # If any error occurs while handling the client request, print an error message
        print(f"Error handling client request: {e}")
    finally:
        # Close the client socket connection, whether the request was successful or not
        client_socket.close()

# Function to start the server, listen for connections, and serve file chunks
def start_server(port, file_chunks):
    # Create a TCP/IP socket (AF_INET for IPv4, SOCK_STREAM for TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the IP address '0.0.0.0' (listen on all available interfaces) and the specified port
    server.bind(('0.0.0.0', port))
    
    # Start listening for incoming connections, allowing up to 5 pending connections
    server.listen(5)
    print(f"Server listening on port {port}...")  # Print a message indicating the server is ready
    logging.info(f"Server listening on port {port}...")


    # Main server loop: keep running and accept client connections
    while True:
        # Accept an incoming connection (blocking call), returns the client socket and address
        client_socket, addr = server.accept()
        logging.info(f"Accepted connection from {addr}")
        # Create a new thread to handle the client request using the `handle_client` function
        # This allows the server to handle multiple clients simultaneously
        client_handler = threading.Thread(target=handle_client, args=(client_socket, file_chunks))
        
        # Start the client handler thread
        client_handler.start()
