# guacd_client.py

import socket
import logging

logger = logging.getLogger('log')

class GuacdClient:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.sock = None
        self.connected = False

    def connect(self):
        try:
            self.sock = socket.create_connection((self.hostname, self.port), timeout=10)
            self.sock.setblocking(False)
            self.connected = True
            logger.info(f'Connected to guacd at {self.hostname}:{self.port}')
        except Exception as e:
            logger.error(f'Failed to connect to guacd: {str(e)}')
            raise e

    def send_instruction(self, instruction):
        if not self.connected or self.sock is None:
            raise Exception("No connection established with guacd.")
        try:
            self.sock.sendall(instruction.encode('utf-8'))
        except Exception as e:
            logger.error(f'Failed to send instruction: {str(e)}')
            self.connected = False
            raise e

    def send_raw(self, data):
        if not self.connected or self.sock is None:
            raise Exception("No connection established with guacd.")
        try:
            self.sock.sendall(data)
        except Exception as e:
            logger.error(f'Failed to send data: {str(e)}')
            self.connected = False
            raise e

    def receive(self):
        if not self.connected or self.sock is None:
            return None
        try:
            data = self.sock.recv(8192)
            if data:
                return data.decode('utf-8', errors='replace')
            else:
                return None
        except BlockingIOError:
            return None
        except Exception as e:
            logger.error(f'Failed to receive data from guacd: {str(e)}')
            self.connected = False
            return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        self.connected = False
        logger.info('Connection to guacd closed.')

    def handshake(self, protocol, connection_parameters):
        try:
            # Step 1: Select protocol
            self.send_instruction(f"0.{len('select')}.{protocol};")
            args_response = self.receive()
            if not args_response or not args_response.startswith('4.args'):
                raise Exception(f"Unexpected response during handshake: {args_response}")

            args = args_response.split(',')[1:]

            # Step 2: Send size
            self.send_instruction(f"0.{len('size')},1,{connection_parameters['width']},{connection_parameters['height']},{connection_parameters['dpi']};")

            # Step 3: Send other required instructions
            # ... (send other instructions as per protocol)

            # Step 4: Send connection parameters
            connect_args = ['connect']
            for arg in args:
                arg_name = arg.split('.')[1]
                value = connection_parameters.get(arg_name, '')
                connect_args.append(value)
            instruction = ','.join(f"{len(arg)}.{arg}" for arg in connect_args) + ';'
            self.send_instruction(instruction)

            # Wait for ready
            ready_response = self.receive()
            if not ready_response or not ready_response.startswith('5.ready'):
                raise Exception(f"Unexpected response: {ready_response}")

            logger.info('Handshake with guacd completed successfully.')

        except Exception as e:
            logger.error(f'Handshake with guacd failed: {str(e)}')
            raise e
