import time
import threading
import logging
from file_utils import chunk_file, rebuild_file, generate_checksum, verify_chunk
from server import start_server
from client import get_chunk_from_peer

# Set up logging
logging.basicConfig(level=logging.INFO)

connected_nodes = []
statistics = {
    'uploaded_file_chunks': 0,
    'downloaded_file_chunks': 0,
    'downloaded_files': 0,
}

# Function to request and download missing chunks from peers
def request_missing_chunks(available_chunks, peer_chunk_map, total_chunks):
    downloaded_chunks = [None] * total_chunks

    for chunk_index in range(total_chunks):
        if chunk_index not in available_chunks:
            for peer, peer_chunks in peer_chunk_map.items():
                if chunk_index in peer_chunks:
                    peer_ip, peer_port = peer.split(":")
                    chunk = get_chunk_from_peer(peer_ip, int(peer_port), chunk_index)
                    if chunk:
                        downloaded_chunks[chunk_index] = chunk
                        logging.info(f"Downloaded chunk {chunk_index} from {peer}")
                        statistics['downloaded_file_chunks'] += 1
                        break
                    else:
                        logging.error(f"Failed to download chunk {chunk_index} from {peer}")
        else:
            downloaded_chunks[chunk_index] = available_chunks[chunk_index]
            logging.info(f"Using local chunk {chunk_index}")

    return downloaded_chunks

def main():
    # Node 4 only handles 4 chunks, so restrict the total number of chunks to 4
    file_chunks = chunk_file('file_to_share.txt', 512)
    file_chunks = file_chunks[:4]  # Node 4 will only handle up to 4 chunks
    total_chunks = len(file_chunks)  # Ensure Node 4 only deals with 4 chunks
    logging.info(f"Total chunks created: {total_chunks}")

    # Node 4 starts with no chunks, so it will need to download all chunks
    available_chunks = {}
    logging.info(f"Node 4 has chunks: {list(available_chunks.keys())}")

    # Node 4 requests chunks from Node 1 and Node 2
    peer_chunk_map = {
        '127.0.0.1:8000': [0, 1],  # Node 1 has chunks 0 and 1
        '127.0.0.1:8001': [2, 3],  # Node 2 has chunks 2 and 3
    }

    # Request the missing chunks from peers
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)

    # If all chunks are successfully downloaded, reconstruct the file
    if None not in downloaded_chunks:
        logging.info(f"Node 4 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        rebuild_file(downloaded_chunks, 'reconstructed_file_node4.txt')
        logging.info("File successfully reconstructed by Node 4.")
        statistics['downloaded_files'] += 1
    else:
        logging.error("Failed to download all chunks.")

if __name__ == '__main__':
    # Start the server for Node 4, which listens on port 8003
    node_4_chunks = []
    threading.Thread(target=start_server, args=(8003, node_4_chunks), daemon=True).start()
    time.sleep(2)
    main()
