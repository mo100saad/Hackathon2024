import time
import threading
import logging
from file_utils import chunk_file, rebuild_file
from server import start_server
from client import get_chunk_from_peer

# Set up logging
logging.basicConfig(level=logging.INFO)

# This function tries to request and download missing file chunks from peers.
def request_missing_chunks(available_chunks, peer_chunk_map, total_chunks):
    # Initialize a list to store downloaded chunks with None (empty slots)
    downloaded_chunks = [None] * total_chunks
    
    # Loop through all the chunks needed for the file
    for chunk_index in range(total_chunks):
        # Check if the current chunk is not available locally
        if chunk_index not in available_chunks:
            # Try to download the missing chunk from peers listed in peer_chunk_map
            for peer, peer_chunks in peer_chunk_map.items():
                if chunk_index in peer_chunks:  # If the peer has the chunk
                    # Split the peer's IP and port for connection
                    peer_ip, peer_port = peer.split(":")
                    # Try to get the chunk from the peer using get_chunk_from_peer function
                    chunk = get_chunk_from_peer(peer_ip, int(peer_port), chunk_index)
                    if chunk:  # If successfully downloaded the chunk
                        downloaded_chunks[chunk_index] = chunk
                        logging.info(f"Downloaded chunk {chunk_index} from {peer}")
                        break  # Stop looking for this chunk once it's downloaded
                    else:  # If download fails, log a failure message
                        logging.error(f"Failed to download chunk {chunk_index} from {peer}")
        else:
            # If chunk is available locally, use it
            downloaded_chunks[chunk_index] = available_chunks[chunk_index]
            logging.info(f"Using local chunk {chunk_index}")
    
    # Return the list of downloaded chunks
    return downloaded_chunks

# Main function to handle the file sharing and reconstruction process
def main():
    # Split the file into chunks using chunk_file function
    file_chunks = chunk_file('file_to_share.txt')

    # Debugging: Log how many chunks were created after splitting the file
    logging.info(f"Total chunks created: {len(file_chunks)}")

    # Create a dictionary to store available chunks for Node 1 (this node)
    # Limiting it to the first 3 chunks to simulate partial availability
    available_chunks = {i: file_chunks[i] for i in range(min(3, len(file_chunks)))}  # Ensure we don't exceed the chunk list

    # Debugging: Log which chunks Node 1 has
    logging.info(f"Node 1 has chunks: {list(available_chunks.keys())}")

    # Define which chunks other peers have
    peer_chunk_map = {
        '127.0.0.1:8001': [i for i in range(3, 6) if i < len(file_chunks)],  # Peers have chunks from 3 to 5
        '127.0.0.1:8002': [i for i in range(6, 9) if i < len(file_chunks)],  # Another peer has chunks from 6 to 8
    }

    # Get the total number of chunks that make up the file
    total_chunks = len(file_chunks)

    # Request missing chunks from peers to complete the file
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)
    
    # Check if all chunks were downloaded successfully (i.e., no None values left)
    if None not in downloaded_chunks:
        # Debugging: Log that the file can now be reconstructed with all chunks
        logging.info(f"Node 1 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        # Rebuild the file using the downloaded chunks
        rebuild_file(downloaded_chunks, 'reconstructed_file_node1.txt')
        logging.info("File successfully reconstructed by Node 1.")
    else:
        # If some chunks are still missing, log an error message
        logging.error("Failed to download all chunks.")

# Start the server in a new thread, which will handle requests for chunks from other peers
if __name__ == '__main__':
    # Node 1 only has chunks 0-2, so only serve those chunks
    node_1_chunks = [chunk_file('file_to_share.txt')[i] for i in range(0, 3) if i < len(chunk_file('file_to_share.txt'))]
    
    # Start a server that listens on port 8000 and serves the local file chunks
    threading.Thread(target=start_server, args=(8000, node_1_chunks)).start()
    
    # Give the server some time to start
    time.sleep(2)
    
    # Start the main file sharing and reconstruction process
    main()
