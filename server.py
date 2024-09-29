import socket
import threading
import logging
from file_utils import chunk_file, generate_checksum, verify_chunk

# Set up logging to display info and error messages
logging.basicConfig(level=logging.INFO)

# Function to handle incoming client requests
def handle_client(client_socket, file_chunks):
    try:
        # Receive the request from the client (up to 1024 bytes) and decode it
        request = client_socket.recv(1024).decode('utf-8')  # Decode the received bytes into a string

        # Check if the request is for a chunk (GET_CHUNK)
        if request.startswith("GET_CHUNK"):
            # Extract the chunk index from the request string (formatted as "GET_CHUNK <chunk_index>")
            chunk_index = int(request.split()[1])

            # Ensure the chunk index is valid (within available chunks)
            if 0 <= chunk_index < len(file_chunks):
                chunk = file_chunks[chunk_index]  # Fetch the requested chunk
                checksum = generate_checksum(chunk)  # Generate a checksum for the chunk

                # Log and send the chunk along with its checksum to the client
                logging.info(f"Serving chunk {chunk_index} with checksum {checksum} to client.")
                client_socket.sendall(chunk + b"||" + checksum.encode('utf-8'))  # Send chunk and checksum

            else:
                # Log a warning and send an empty response if the requested chunk is invalid
                logging.warning(f"Invalid chunk request for index {chunk_index}.")
                client_socket.sendall(b'')  # Send an empty response if the index is out of bounds

        # Check if the client is requesting chunk verification (VERIFY_CHUNK)
        elif request.startswith("VERIFY_CHUNK"):
            # Extract the chunk index and the checksum received by the client
            chunk_index, received_checksum = request.split()[1:]
            chunk_index = int(chunk_index)
            
            # Ensure the chunk index is valid (within available chunks)
            if 0 <= chunk_index < len(file_chunks):
                chunk = file_chunks[chunk_index]  # Fetch the chunk for verification
                valid = verify_chunk(chunk, received_checksum)  # Verify the client's checksum

                # If the chunk is not valid (checksum mismatch), retransmit the chunk
                if not valid:
                    logging.info(f"Retransmitting chunk {chunk_index} due to checksum mismatch.")
                    client_socket.sendall(chunk + b"||" + generate_checksum(chunk).encode('utf-8'))  # Resend chunk
                else:
                    # If the chunk is valid, notify the client that no retransmission is needed
                    logging.info(f"Chunk {chunk_index} verified successfully. No retransmission needed.")
                    client_socket.sendall(b'OK')  # Send 'OK' to indicate success

    except socket.error as e:
        # Log socket-related errors, such as connection issues
        logging.error(f"Socket error: {e}")

    except Exception as e:
        # Log any other general errors encountered while handling the client request
        logging.error(f"Error handling client request: {e}")

    finally:
        # Close the client connection after the request is handled or if an error occurs
        client_socket.close()

# Function to start the server, listen for incoming connections, and serve file chunks
def start_server(port, file_chunks):
    # Create a TCP/IP socket (AF_INET for IPv4, SOCK_STREAM for TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Bind the socket to the specified IP address (0.0.0.0) and port, allowing connections from all interfaces
        server.bind(('0.0.0.0', port))
        
        # Start listening for incoming client connections (up to 5 pending connections allowed)
        server.listen(5)
        logging.info(f"Server listening on port {port}...")  # Log that the server is ready to accept connections

        # Main server loop: keep running and accept client connections
        while True:
            # Accept an incoming connection, returning the client socket and address
            client_socket, addr = server.accept()
            logging.info(f"Accepted connection from {addr}")  # Log the client's IP address and port

            # Create a new thread to handle the client's request using the handle_client function
            client_handler = threading.Thread(target=handle_client, args=(client_socket, file_chunks))
            
            # Start the client handler thread to handle the client's request
            client_handler.start()

    except Exception as e:
        # Log any errors that occur during server operation, such as binding issues or connection failures
        logging.error(f"Server error: {e}")

    finally:
        # Ensure that the server socket is closed when the server shuts down
        server.close()
        logging.info("Server has been shut down.")  # Log that the server has stopped
