import time
import threading
import logging
from file_utils import chunk_file, rebuild_file
from server import start_server
from client import get_chunk_from_peer

logging.basicConfig(level=logging.INFO)

# This function requests missing chunks from peers and downloads them if they are missing locally.
def request_missing_chunks(available_chunks, peer_chunk_map, total_chunks):
    # Initialize the list for storing the downloaded chunks, all set to None initially
    downloaded_chunks = [None] * total_chunks
    
    # Loop through all chunks to check if they are available locally or need to be downloaded
    for chunk_index in range(total_chunks):
        # If the current chunk is missing (not in available_chunks), try to download it
        if chunk_index not in available_chunks:
            # Loop through the peer chunk map to find a peer that has the missing chunk
            for peer, peer_chunks in peer_chunk_map.items():
                if chunk_index in peer_chunks:  # Check if the peer has the chunk
                    # Get the peer's IP address and port
                    peer_ip, peer_port = peer.split(":")
                    # Attempt to get the chunk from the peer
                    chunk = get_chunk_from_peer(peer_ip, int(peer_port), chunk_index)
                    if chunk:  # If the chunk was successfully downloaded
                        downloaded_chunks[chunk_index] = chunk
                        logging.info(f"Downloaded chunk {chunk_index} from {peer}")
                        break  # Stop looking for the chunk once it's downloaded
                    else:
                        logging.error(f"Failed to download chunk {chunk_index} from {peer}")
        else:
            # If Node 4 already has the chunk, no need to download it
            downloaded_chunks[chunk_index] = available_chunks[chunk_index]
            logging.info(f"Using local chunk {chunk_index}")
    
    # Return the list of chunks, which now includes both local and downloaded chunks
    return downloaded_chunks

# Main function to handle the file-sharing and reconstruction process for Node 4
def main():
    # Split the file into chunks using the chunk_file function
    file_chunks = chunk_file('file_to_share.txt')
    
    # Debugging: Print the total number of chunks that were created
    logging.info(f"Total chunks created: {len(file_chunks)}")

    # Define which chunks Node 4 already has (in this case, chunks 9, 10, and 11)
    available_chunks = {i: file_chunks[i] for i in range(9, 12) if i < len(file_chunks)}

    # Debugging: Print the chunks that Node 4 has locally
    logging.info(f"Node 4 has chunks: {list(available_chunks.keys())}")

    # Define the peer chunk map, which lists what chunks other peers have
    peer_chunk_map = {
        '127.0.0.1:8000': [i for i in range(0, 3) if i < len(file_chunks)],  # Node 1 has chunks 0-2
        '127.0.0.1:8001': [i for i in range(3, 6) if i < len(file_chunks)],  # Node 2 has chunks 3-5
        '127.0.0.1:8002': [i for i in range(6, 9) if i < len(file_chunks)],  # Node 3 has chunks 6-8
    }

    # Get the total number of chunks that make up the file
    total_chunks = len(file_chunks)

    # Request and download any missing chunks from peers in the network
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)
    
    # Check if all chunks have been successfully downloaded (i.e., no None values remain)
    if None not in downloaded_chunks:
        # Debugging: Print the chunk indices used to reconstruct the file
        logging.info(f"Node 4 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        # Rebuild the file from the chunks and save it as 'reconstructed_file_node4.txt'
        rebuild_file(downloaded_chunks, 'reconstructed_file_node4.txt')
        logging.info("File successfully reconstructed by Node 4.")
        
    else:
        # If some chunks are still missing, print an error message
        logging.error("Failed to download all chunks.")

# When this script is run, start the server in a new thread
if __name__ == '__main__':
    # Node 4 only has chunks 9-11, so only serve those chunks
    node_4_chunks = [chunk_file('file_to_share.txt')[i] for i in range(9, 12) if i < len(chunk_file('file_to_share.txt'))]
    
    # Start the server that listens on port 8003 for chunk requests from other peers
    threading.Thread(target=start_server, args=(8003, node_4_chunks)).start()
    
    # Allow some time for the server to start before requesting chunks from peers
    time.sleep(2)
    
    # Run the main function to start the file-sharing and reconstruction process for Node 4
    main()
