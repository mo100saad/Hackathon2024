import logging
import hashlib

# Set up logging to display informational messages
logging.basicConfig(level=logging.INFO)


# Function to compute the hash of a file for integrity verification
def compute_file_hash(file_path, chunk_size=512):
    # Initialize a SHA-256 hash function
    hash_func = hashlib.sha256()
    
    # Open the file in binary read mode
    with open(file_path, 'rb') as f:
        # Read the file in chunks of the specified size (default 512 bytes)
        while chunk := f.read(chunk_size):
            # Update the hash with the content of each chunk
            hash_func.update(chunk)
    
    # Return the computed hash as a hexadecimal string
    return hash_func.hexdigest()

# Function to split a file into chunks
def chunk_file(file_path, chunk_size=512):
    # Initialize a list to store the file chunks
    chunks = []
    
    # Open the file in binary read mode
    with open(file_path, 'rb') as f:
        # Initialize chunk index for logging purposes
        chunk_index = 0
        
        # Read the file in chunks of the specified size (default 512 bytes)
        while chunk := f.read(chunk_size):
            # Log the size and index of each chunk being read
            logging.info(f"Chunking: Read chunk {chunk_index} of size {len(chunk)} bytes.")
            
            # Append the chunk to the list of chunks
            chunks.append(chunk)
            
            # Increment the chunk index
            chunk_index += 1
    
    # Log the total number of chunks created
    logging.info(f"Total chunks created: {chunk_index}")
    
    # Return the list of file chunks
    return chunks

# Function to rebuild a file from chunks
def rebuild_file(chunks, output_file):
    # Open the output file in binary write mode
    with open(output_file, 'wb') as f:
        # Loop through each chunk and write it to the output file
        for i, chunk in enumerate(chunks):
            # Log the size and index of each chunk being written
            logging.info(f"Rebuilding: Writing chunk {i} of size {len(chunk)} bytes.")
            
            # Write the chunk to the file
            f.write(chunk)
    
    # Log a message when the file reconstruction is complete
    logging.info(f"File reconstruction complete: {output_file}")
