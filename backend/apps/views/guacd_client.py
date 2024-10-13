# guacd_client.py

import socket
import logging
import select
import errno
import time

logger = logging.getLogger('log')

class GuacdClient:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.sock = None
        self.connected = False

    def connect(self):
        """
        Establishes a socket connection to the guacd server.
        """
        try:
            self.sock = socket.create_connection((self.hostname, self.port), timeout=10)
            self.sock.setblocking(False)  # 设置为非阻塞模式
            self.connected = True
            logger.info(f'Connected to guacd at {self.hostname}:{self.port}')
        except Exception as e:
            logger.error(f'Failed to connect to guacd: {str(e)}')
            raise e

    def send_instruction(self, instruction):
        """
        Sends an instruction to guacd.
        """
        if not self.connected or self.sock is None:
            raise Exception("No connection established with guacd.")
        
        try:
            # Add length prefixes to each part of the instruction
            parts = instruction.split(',')
            length_prefixed_parts = [f"{len(part)}.{part}" for part in parts]
            full_instruction = f"{','.join(length_prefixed_parts)};"
            
            logger.debug(f'Sending instruction: {full_instruction}')
            self.sock.sendall(full_instruction.encode('utf-8'))
        except Exception as e:
            logger.error(f'Failed to send instruction: {str(e)}')
            self.connected = False
            raise e

    def receive(self):
        """
        Receives data from guacd.
        """
        if not self.connected or self.sock is None:
            return None

        try:
            ready = select.select([self.sock], [], [], 5)
            if ready[0]:
                data = b''
                last_activity = time.time()
                while not data.endswith(b';'):
                    try:
                        chunk = self.sock.recv(4096)
                        if not chunk:
                            if time.time() - last_activity > 10:  # 10秒无活动
                                if not self.send_heartbeat():
                                    self.connected = False
                                    return None
                            continue
                        data += chunk
                        last_activity = time.time()
                    except socket.error as e:
                        err = e.args[0]
                        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                            if time.time() - last_activity > 10:  # 10秒无活动
                                if not self.send_heartbeat():
                                    self.connected = False
                                    return None
                            continue
                        else:
                            self.connected = False
                            raise
                return data.decode('utf-8', errors='replace')
            else:
                if not self.send_heartbeat():
                    self.connected = False
                return None
        except Exception as e:
            logger.error(f'Failed to receive data from guacd: {str(e)}')
            self.connected = False
            return None

    def close(self):
        """
        Closes the connection to guacd.
        """
        if self.sock:
            self.sock.close()
            self.sock = None
        self.connected = False
        logger.info('Connection to guacd closed.')

    def handshake(self, protocol, connection_parameters):
        """
        Performs the Guacamole handshake with guacd.
        """
        try:
            # Step 1: Select protocol
            self.send_instruction(f'select,{protocol}')
            args_response = self.receive()
            
            # Parse args response
            if not args_response.startswith('4.args'):
                raise Exception(f"Unexpected response during handshake: {args_response}")
            
            args = args_response.split(',')[1:]
            
            # Step 2: Send size
            self.send_instruction(f'size,1,{connection_parameters["width"]},{connection_parameters["height"]},{connection_parameters["dpi"]}')
            
            # Step 3: Send audio support
            self.send_instruction('audio,0')
            
            # Step 4: Send video support
            self.send_instruction('video')
            
            # Step 5: Send image support
            self.send_instruction('image,0,image/png,image/jpeg')

            # Step 6: Send connection parameters
            connect_args = ['connect']
            for arg in args:
                arg_name = arg.split('.')[1]
                value = connection_parameters.get(arg_name, '')
                connect_args.append(value)
            
            self.send_instruction(','.join(connect_args))
            
            # Wait for ready
            ready_response = self.receive()
            if not ready_response.startswith('5.ready'):
                raise Exception(f"Unexpected response: {ready_response}")
            
            logger.info('Handshake with guacd completed successfully.')

        except Exception as e:
            logger.error(f'Handshake with guacd failed: {str(e)}')
            raise e

    def send_heartbeat(self):
        """
        Sends a heartbeat to keep the connection alive.
        """
        try:
            self.send_instruction('nop')
            return True
        except:
            return False
