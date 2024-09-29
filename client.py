import socket
import logging

logging.basicConfig(level=logging.INFO)

# Function to request a chunk of data from a peer
def get_chunk_from_peer(peer_ip, peer_port, chunk_index):
    try:
        # Create a new socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a timeout for the socket connection (5 seconds)
        client.settimeout(5)
        
        # Connect to the peer using the provided IP address and port
        client.connect((peer_ip, peer_port))
        
        # Send a request for the chunk, formatted as "GET_CHUNK <chunk_index>"
        client.sendall(f"GET_CHUNK {chunk_index}".encode('utf-8'))  # Encode the request into bytes
        
        # Receive the chunk data from the peer (with a buffer size of 512 bytes)
        chunk = client.recv(512)
        
        # Close the connection after receiving the data
        client.close()
        if chunk:
            logging.info(f"Successfully downloaded chunk {chunk_index} from {peer_ip}:{peer_port}")
            
        # Return the chunk if it's not empty, otherwise return None
        return chunk if chunk else None
    
    # Handle socket timeout errors (e.g., if the peer does not respond in time)
    except socket.timeout:
        print(f"Connection to {peer_ip}:{peer_port} timed out.")
        logging.error(f"Connection to {peer_ip}:{peer_port} timed out.")

    # Handle any other exceptions that might occur (e.g., connection errors, send/receive errors)
    except Exception as e:
        print(f"Error fetching chunk from {peer_ip}:{peer_port}: {e}")
        logging.error(f"Error fetching chunk from {peer_ip}:{peer_port}: {e}")

    # Return None if an error occurs or the chunk could not be fetched
    return None
