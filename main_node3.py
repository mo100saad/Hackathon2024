import time
import threading
import logging
from file_utils import chunk_file, rebuild_file
from server import start_server
from client import get_chunk_from_peer

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to request missing chunks from peers
def request_missing_chunks(available_chunks, peer_chunk_map, total_chunks):
    # Initialize a list for storing the downloaded chunks, initially set to None
    downloaded_chunks = [None] * total_chunks
    
    # Iterate through each chunk needed for the file
    for chunk_index in range(total_chunks):
        # If the chunk is missing locally (i.e., not in available_chunks)
        if chunk_index not in available_chunks:
            # Loop through peers to try and download the missing chunk
            for peer, peer_chunks in peer_chunk_map.items():
                # Check if the peer has the chunk we are looking for
                if chunk_index in peer_chunks:
                    # Extract peer IP and port
                    peer_ip, peer_port = peer.split(":")
                    # Attempt to download the chunk from the peer
                    chunk = get_chunk_from_peer(peer_ip, int(peer_port), chunk_index)
                    if chunk:  # If the chunk is successfully downloaded
                        downloaded_chunks[chunk_index] = chunk
                        logging.info(f"Downloaded chunk {chunk_index} from {peer}")
                        break  # Stop trying other peers for this chunk
                    else:
                        logging.error(f"Failed to download chunk {chunk_index} from {peer}")
        else:
            # If we already have the chunk locally, no need to download it
            downloaded_chunks[chunk_index] = available_chunks[chunk_index]
            logging.info(f"Using local chunk {chunk_index}")
    
    # Return the list of chunks, which now includes both local and downloaded chunks
    return downloaded_chunks

# Main function to handle file sharing and reconstruction for Node 3
def main():
    # Split the file into chunks using the chunk_file function
    file_chunks = chunk_file('file_to_share.txt')
    
    # Debugging: Log the total number of chunks that were created
    logging.info(f"Total chunks created: {len(file_chunks)}")

    # Define the chunks that Node 3 has (in this case, chunks 6, 7, and 8)
    available_chunks = {i: file_chunks[i] for i in range(6, 9) if i < len(file_chunks)}

    # Debugging: Log the chunks that Node 3 has locally
    logging.info(f"Node 3 has chunks: {list(available_chunks.keys())}")

    # Map of peers and the chunks they hold, used by Node 3 to request missing chunks
    peer_chunk_map = {
        '127.0.0.1:8000': [i for i in range(0, 3) if i < len(file_chunks)],  # Node 1 has chunks 0-2
        '127.0.0.1:8001': [i for i in range(3, 6) if i < len(file_chunks)],  # Node 2 has chunks 3-5
    }

    # Get the total number of chunks that make up the file
    total_chunks = len(file_chunks)

    # Request and download missing chunks from the peers in the network
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)
    
    # If all chunks are successfully downloaded (i.e., no None values remain)
    if None not in downloaded_chunks:
        # Debugging: Log the indices of the chunks used to reconstruct the file
        logging.info(f"Node 3 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        # Rebuild the file using the downloaded chunks and save it as 'reconstructed_file_node3.txt'
        rebuild_file(downloaded_chunks, 'reconstructed_file_node3.txt')
        logging.info("File successfully reconstructed by Node 3.")
    else:
        # If some chunks are still missing, log an error message
        logging.error("Failed to download all chunks.")

# When this script is run, start the server in a new thread
if __name__ == '__main__':
    # Node 3 only has chunks 6-8, so only serve those chunks
    node_3_chunks = [chunk_file('file_to_share.txt')[i] for i in range(6, 9) if i < len(chunk_file('file_to_share.txt'))]
    
    # Start the server for Node 3, which listens on port 8002 and serves its chunks
    threading.Thread(target=start_server, args=(8002, node_3_chunks)).start()
    
    # Allow some time for the server to start before proceeding
    time.sleep(2)
    
    # Run the main function to handle the file sharing process for Node 3
    main()
