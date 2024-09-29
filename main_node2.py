import time
import threading
import logging
from file_utils import chunk_file, rebuild_file, generate_checksum, verify_chunk
from server import start_server
from client import get_chunk_from_peer

# Set up logging
logging.basicConfig(level=logging.INFO)

# List of connected nodes and statistics tracking
connected_nodes = []
statistics = {
    'uploaded_file_chunks': 0,
    'downloaded_file_chunks': 0,
    'downloaded_files': 0,
}

# Function to request missing chunks from peers
def request_missing_chunks(available_chunks, peer_chunk_map, total_chunks):
    downloaded_chunks = [None] * total_chunks  # Initialize an empty list for downloaded chunks
    
    # Loop through all the chunks and download those that are missing
    for chunk_index in range(total_chunks):
        if chunk_index not in available_chunks:
            # Try to download the missing chunk from peers
            for peer, peer_chunks in peer_chunk_map.items():
                if chunk_index in peer_chunks:  # If a peer has the chunk
                    peer_ip, peer_port = peer.split(":")
                    # Attempt to download the chunk from the peer
                    chunk = get_chunk_from_peer(peer_ip, int(peer_port), chunk_index)
                    if chunk:  # If the chunk is successfully downloaded
                        downloaded_chunks[chunk_index] = chunk
                        logging.info(f"Downloaded chunk {chunk_index} from {peer}")
                        statistics['downloaded_file_chunks'] += 1
                        break  # Exit the loop once the chunk is downloaded
                    else:
                        logging.error(f"Failed to download chunk {chunk_index} from {peer}")
        else:
            # If the chunk is available locally, use it
            downloaded_chunks[chunk_index] = available_chunks[chunk_index]
            logging.info(f"Using local chunk {chunk_index}")

    return downloaded_chunks

# Main function for file-sharing and reconstruction
def main():
    # Split the file into chunks of 512 bytes
    file_chunks = chunk_file('file_to_share.txt', 512)
    logging.info(f"Total chunks created: {len(file_chunks)}")

    # Node 2 has chunks 2 and 3
    available_chunks = {i: file_chunks[i] for i in range(2, 4) if i < len(file_chunks)}
    logging.info(f"Node 2 has chunks: {list(available_chunks.keys())}")

    # Peer chunk map (Node 1 has chunks 0 and 1)
    peer_chunk_map = {
        '127.0.0.1:8000': [0, 1],  # Node 1 has chunks 0 and 1
    }

    total_chunks = len(file_chunks)  # Total number of chunks in the file (should be 4)

    # Request missing chunks from peers
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)

    # If all chunks are successfully downloaded, reconstruct the file
    if None not in downloaded_chunks:
        logging.info(f"Node 2 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        rebuild_file(downloaded_chunks, 'reconstructed_file_node2.txt')
        logging.info("File successfully reconstructed by Node 2.")
        statistics['downloaded_files'] += 1
    else:
        logging.error("Failed to download all chunks.")

# Entry point for the Node 2 script
if __name__ == '__main__':
    # Node 2 serves chunks 2 and 3
    node_2_chunks = [chunk_file('file_to_share.txt', 512)[i] for i in range(2, 4) if i < len(chunk_file('file_to_share.txt', 512))]

    # Start the server for Node 2 (listening on port 8001), running as a daemon thread
    threading.Thread(target=start_server, args=(8001, node_2_chunks), daemon=True).start()
    
    # Allow some time for the server to start before proceeding
    time.sleep(2)
    
    # Run the main file sharing and reconstruction function
    main()
