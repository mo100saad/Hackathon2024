import time
import threading
import logging
from file_utils import chunk_file, rebuild_file, generate_checksum, verify_chunk
from server import start_server
from client import get_chunk_from_peer

# Set up logging
logging.basicConfig(level=logging.INFO)

connected_nodes = []  # List to track connected nodes
statistics = {
    'uploaded_file_chunks': 0,
    'downloaded_file_chunks': 0,
    'downloaded_files': 0,
}

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
    file_chunks = chunk_file('file_to_share.txt', 512)  # Chunk size of 512 bytes
    logging.info(f"Total chunks created: {len(file_chunks)}")

    available_chunks = {i: file_chunks[i] for i in range(0, 4) if i < len(file_chunks)}  # First 4 chunks
    logging.info(f"Node 1 has chunks: {list(available_chunks.keys())}")

    peer_chunk_map = {
        'proxy22.rt3.io:38788': [i for i in range(4, 8) if i < len(file_chunks)], #Zack
        'proxy17.rt3.io:33403': [i for i in range(8, 12) if i < len(file_chunks)], #Roshan
        'proxy17.rt3.io:33408': [i for i in range(12, 16) if i < len(file_chunks)], #Harsh
    }

    total_chunks = len(file_chunks)
    downloaded_chunks = request_missing_chunks(available_chunks, peer_chunk_map, total_chunks)

    if None not in downloaded_chunks:
        logging.info(f"Node 1 is reconstructing the file with chunks: {list(range(len(downloaded_chunks)))}")
        rebuild_file(downloaded_chunks, 'reconstructed_file_node1.txt')
        logging.info("File successfully reconstructed by Node 1.")
        statistics['downloaded_files'] += 1
    else:
        logging.error("Failed to download all chunks.")

if __name__ == '__main__':
    node_1_chunks = [chunk_file('file_to_share.txt', 512)[i] for i in range(0, 4) if i < len(chunk_file('file_to_share.txt', 512))]
    threading.Thread(target=start_server, args=(8000, node_1_chunks)).start()
    time.sleep(2)
    main()
