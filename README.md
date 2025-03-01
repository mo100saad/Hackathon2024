# Peer-to-Peer Networking System

![Testing Running Image!](images/netowrk.jpeg)

The Peer-to-Peer (P2P) Networking System is a Python-based client-server application designed for seamless, real-time communication among multiple nodes. Each node acts as both a client and a server, utilizing TCP/IP protocols, socket programming, and threading libraries to handle data exchange and concurrency efficiently.

## Overview

This project demonstrates a P2P architecture where a fixed number of nodes communicate directly with each other. The system is optimized for:
- **Real-Time Communication:** Low-latency data transfer.
- **Concurrent Operations:** Handling multiple connections with Python’s threading.
- **Robust Error Handling:** Recovering gracefully from network disruptions.
- **Modularity:** An extendable codebase that allows future scalability.

## Features

- **Dual Role Nodes:** Each node functions as both a client and a server.
- **TCP/IP Communication:** Reliable, protocol-based data exchange.
- **Multithreading:** Efficient management of simultaneous connections.
- **Dynamic Data Exchange:** Real-time message and data packet sharing.
- **Error Recovery:** Built-in mechanisms to manage connection issues.
- **Modular Code Structure:** Easily maintainable and extendable.

## Architecture

### Node Structure

- **Server Component:** Listens for incoming connections and processes requests from other nodes.
- **Client Component:** Initiates connections to other nodes for sending and receiving data.
- **Thread Manager:** Uses Python’s `threading` module to concurrently manage multiple connections.
- **Socket Interface:** Employs TCP/IP sockets for reliable data transmission.

### Data Flow

1. **Initialization:** Each node starts its server component and spawns threads for handling client requests.
2. **Connection Establishment:** Nodes connect with one another using TCP.
3. **Data Exchange:** Nodes exchange messages and data packets in real time.
4. **Error Handling:** The system logs and manages errors, attempting reconnections as necessary.

## Prerequisites

Before running the application, ensure you have:
- Python 3.7 or higher.
- Required Python libraries (listed in `requirements.txt`):
  - `socket`
  - `threading`

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/p2p-network-project.git
   cd p2p-network-project
