import socket
import logging
from file_utils import generate_checksum, verify_chunk

logging.basicConfig(level=logging.INFO)

# Function to request a chunk of data from a peer with retry logic
def get_chunk_from_peer(peer_ip, peer_port, chunk_index, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            # Create a new socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set a timeout for the socket connection (5 seconds)
            client.settimeout(5)
            
            # Connect to the peer using the provided IP address and port
            client.connect((peer_ip, peer_port))
            
            # Send a request for the chunk, formatted as "GET_CHUNK <chunk_index>"
            client.sendall(f"GET_CHUNK {chunk_index}".encode('utf-8'))  # Encode the request into bytes
            
            # Receive the chunk data and the checksum from the peer (with a buffer size of 512 bytes for chunk and checksum)
            response = client.recv(1024)  # We assume the chunk and checksum are sent together
            client.close()

            # Split the chunk data and checksum (assuming they are separated by ||)
            chunk, checksum = response.split(b'||')
            
            # Log and validate the checksum of the received chunk
            if verify_chunk(chunk, checksum.decode('utf-8')):  # Verify if the checksum matches
                logging.info(f"Successfully downloaded and verified chunk {chunk_index} from {peer_ip}:{peer_port}")
                return chunk  # Return the valid chunk
            else:
                logging.warning(f"Checksum mismatch for chunk {chunk_index} from {peer_ip}:{peer_port}. Retrying...")
        
        # Handle socket timeout errors (e.g., if the peer does not respond in time)
        except socket.timeout:
            logging.error(f"Connection to {peer_ip}:{peer_port} timed out on attempt {attempt + 1}/{retries}. Retrying...")
        
        # Handle any other exceptions that might occur (e.g., connection errors, send/receive errors)
        except Exception as e:
            logging.error(f"Error fetching chunk {chunk_index} from {peer_ip}:{peer_port}: {e}")
        
        finally:
            # Increment the attempt count and retry
            attempt += 1

    # Return None if the chunk could not be fetched after all retry attempts
    logging.error(f"Failed to download chunk {chunk_index} from {peer_ip}:{peer_port} after {retries} attempts.")
    return None
