# guacamole_client.py

import socket

class GuacamoleClient:
    def __init__(self, hostname, port):
        self.socket = socket.create_connection((hostname, port))
        self.socket_file = self.socket.makefile('rwb', buffering=0)
    
    def handshake(self, protocol, parameters):
        # Send protocol version
        self.send_instruction('select', protocol)

        # Receive server args
        opcode, args = self.receive_instruction()
        if opcode != 'args':
            raise Exception(f'Expected "args" instruction, got "{opcode}"')

        # Prepare parameters
        param_values = [parameters.get(arg, '') for arg in args]

        # Send connect instruction
        self.send_instruction('connect', *param_values)

    def send_instruction(self, opcode, *args):
        instruction = f'{opcode}'
        for arg in args:
            instruction += f',{arg}'
        instruction += ';'
        self.socket_file.write(instruction.encode('utf-8'))

    def receive_instruction(self):
        data = ''
        while True:
            char = self.socket_file.read(1).decode('utf-8')
            if char == ';':
                break
            data += char
        parts = data.split(',')
        opcode = parts[0]
        args = parts[1:]
        return opcode, args

    def send(self, data):
        self.socket_file.write(data.encode('utf-8'))

    def receive(self):
        return self.socket_file.read(8192).decode('utf-8')

    def close(self):
        self.socket.close()
