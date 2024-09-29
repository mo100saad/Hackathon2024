import time
import threading
import logging
from file_utils import chunk_file, rebuild_file, generate_checksum, verify_chunk
from server import start_server
from client import get_chunk_from_peer

# Set up logging
logging.basicConfig(level=logging.INFO)

# Connected nodes and statistics tracking
connected_nodes = []  # List to track connected nodes
statistics = {
    'uploaded_file_chunks': 0,
    'downloaded_file_chunks': 0,
    'downloaded_files': 0,
}

# Function to request and download missing chunks from peers
def request_missing_chunks(available_chunks, peer_chunk_map, total_chunks):
    downloaded_chunks = [None] * total_chunks  # Initialize the list of downloaded chunks
    
    # Loop over all chunks and determine if they need to be downloaded
    for chunk_index in range(total_chunks):
        if chunk_index not in available_chunks:  # If this chunk is not available locally
            # Try to download the missing chunk from peers
            for peer, peer_chunks in peer_chunk_map.items():
                if chunk_index in peer_chunks:  # Check if the peer has the chunk
                    peer_ip, peer_port = peer.split(":")
                    # Try to fetch the chunk from the peer
                    chunk = get_chunk_from_peer(peer_ip, int(peer_port), chunk_index)
                    if chunk:  # If chunk is successfully downloaded
                        downloaded_chunks[chunk_index] = chunk
                        logging.info(f"Downloaded chunk {chunk_index} from {peer}")
                        statistics['downloaded_file_chunks'] += 1
                        break  # Exit loop once the chunk is downloaded
                    else:
                        logging.error(f"Failed to download chunk {chunk_index} from {peer}")
        else:
            # If we already have the chunk locally, just use it
            downloaded_chunks[chunk_index] = available_chunks[chunk_index]
            logging.info(f"Using local chunk {chunk_index}")
    
    return downloaded_chunks

# Function to handle file reconstruction
def main():
    # Split the file into chunks of 512 bytes
    file_chunks = chunk_file('file_to_share.txt', 512)
    
    # Ensure Node 1 handles only 4 chunks total (even if more chunks exist in the system)
    file_chunks = file_chunks[:4]  # Node 1 will only deal with chunks 0-3
    total_chunks = len(file_chunks)  # Limit total_chunks to 4
    logging.info(f"Total chunks created: {total_chunks}")

    # Node 1 has the first 4 chunks (chunks 0-3)
    available_chunks = {i: file_chunks[i] for i in range(0, 4) if i < total_chunks}
    logging.info(f"Node 1 has chunks: {list(available_chunks.keys())}")

    # Define the peer chunk map with IP addresses of other peers (if needed)
    peer_chunk_map = {
        '127.0.0.1:8001': [2, 3],  # Node 2 (which has chunks 2-3)
    }

    # Request the missing chunks from peers (up to 4 chunks total)
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)

    # If all chunks are successfully downloaded, reconstruct the file
    if None not in downloaded_chunks:
        logging.info(f"Node 1 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        rebuild_file(downloaded_chunks, 'reconstructed_file_node1.txt')
        logging.info("File successfully reconstructed by Node 1.")
        statistics['downloaded_files'] += 1
    else:
        logging.error("Failed to download all chunks.")

# Entry point for the Node 1 script
if __name__ == '__main__':
    # Node 1 has chunks 0-3, so only serve those
    node_1_chunks = [chunk_file('file_to_share.txt', 512)[i] for i in range(0, 4) if i < len(chunk_file('file_to_share.txt', 512))]

    # Start the server for Node 1, which listens on port 8000 and serves its chunks
    threading.Thread(target=start_server, args=(8000, node_1_chunks), daemon=True).start()

    # Allow some time for the server to start before proceeding
    time.sleep(2)

    # Run the main function to handle file sharing and reconstruction
    main()
