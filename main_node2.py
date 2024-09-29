import time
import threading
import logging
from file_utils import chunk_file, rebuild_file
from server import start_server
from client import get_chunk_from_peer

# Set up logging
logging.basicConfig(level=logging.INFO)

# This function requests and downloads any missing file chunks from other peers.
def request_missing_chunks(available_chunks, peer_chunk_map, total_chunks):
    # Initialize a list to store downloaded chunks, initially all set to None
    downloaded_chunks = [None] * total_chunks
    
    # Iterate through the required chunks
    for chunk_index in range(total_chunks):
        # If the current chunk is not available locally in Node 2
        if chunk_index not in available_chunks:
            # Try to download the missing chunk from peers listed in peer_chunk_map
            for peer, peer_chunks in peer_chunk_map.items():
                if chunk_index in peer_chunks:  # If the peer has the chunk
                    # Extract the peer's IP address and port for communication
                    peer_ip, peer_port = peer.split(":")
                    # Request the chunk from the peer
                    chunk = get_chunk_from_peer(peer_ip, int(peer_port), chunk_index)
                    if chunk:  # If the chunk was successfully downloaded
                        downloaded_chunks[chunk_index] = chunk
                        logging.info(f"Downloaded chunk {chunk_index} from {peer}")
                        break  # Stop trying other peers once the chunk is downloaded
                    else:
                        logging.error(f"Failed to download chunk {chunk_index} from {peer}")
        else:
            # If Node 2 already has the chunk, use it
            downloaded_chunks[chunk_index] = available_chunks[chunk_index]
            logging.info(f"Using local chunk {chunk_index}")
    
    # Return the list of all downloaded (or locally available) chunks
    return downloaded_chunks

# Main function that handles Node 2's file sharing and reconstruction process
def main():
    # Split the file into chunks using the chunk_file function
    file_chunks = chunk_file('file_to_share.txt')
    
    # Debugging: Log how many chunks the file was split into
    logging.info(f"Total chunks created: {len(file_chunks)}")

    # Define which chunks Node 2 already has (in this case, chunks 3, 4, and 5)
    available_chunks = {i: file_chunks[i] for i in range(3, 6) if i < len(file_chunks)}

    # Debugging: Log which chunks Node 2 has locally
    logging.info(f"Node 2 has chunks: {list(available_chunks.keys())}")

    # Peer chunk map, indicating which other nodes have which chunks
    peer_chunk_map = {
        '127.0.0.1:8000': [i for i in range(0, 3) if i < len(file_chunks)],  # Node 1 has chunks 0, 1, and 2
        '127.0.0.1:8002': [i for i in range(6, 9) if i < len(file_chunks)],  # Another peer has chunks 6, 7, and 8
    }

    # Get the total number of chunks that make up the file
    total_chunks = len(file_chunks)

    # Request and download any missing chunks from peers
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)
    
    # Check if all chunks have been successfully downloaded (i.e., no None values remain)
    if None not in downloaded_chunks:
        # Debugging: Log the indices of all the chunks Node 2 now has (including downloaded)
        logging.info(f"Node 2 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        # Rebuild the original file using the downloaded chunks
        rebuild_file(downloaded_chunks, 'reconstructed_file_node2.txt')
        logging.info("File successfully reconstructed by Node 2.")
    else:
        # If some chunks are still missing, log a failure message
        logging.error("Failed to download all chunks.")

# When this script is run, start a server in a new thread
if __name__ == '__main__':
    # Node 2 only has chunks 3-5, so only serve those chunks
    node_2_chunks = [chunk_file('file_to_share.txt')[i] for i in range(3, 6) if i < len(chunk_file('file_to_share.txt'))]
    
    # Start the server that listens on port 8001 for requests for the file chunks Node 2 has
    threading.Thread(target=start_server, args=(8001, node_2_chunks)).start()
    
    # Wait for the server to start before proceeding with file requests
    time.sleep(2)
    
    # Run the main function that handles file sharing and reconstruction
    main()
