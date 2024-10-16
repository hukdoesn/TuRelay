import socket

class GuacamoleClient:
    def __init__(self, guacd_host='localhost', guacd_port=4822):
        self.guacd_host = guacd_host
        self.guacd_port = guacd_port
        self.sock = None
        self.connected = False

    def connect(self, protocol, hostname, username, password, port=3389):
        """连接到 guacd 并完成握手过程"""
        try:
            # 打印调试信息，确保传递的参数正确
            print(f"GuacamoleClient connecting with the following parameters:")
            print(f"Protocol: {protocol}")
            print(f"Hostname: {hostname}")
            print(f"Port: {port}")
            print(f"Username: {username}")
            print(f"Password: {password}")

            self.sock = socket.create_connection((self.guacd_host, self.guacd_port))
            self.connected = True

            # 1. 发送 'select' 指令，选择协议
            self._send_instruction('select', [protocol])

            # 2. 接收服务器请求的参数列表
            instruction = self._read_instruction()
            if instruction[0] != 'args':
                raise Exception(f"Expected 'args' instruction, but got '{instruction[0]}'")

            requested_args = instruction[1:]
            print(f"Server requested args: {requested_args}")

            # 3. 根据服务器请求的参数列表，按顺序提供参数值
            args_values = []
            for arg_name in requested_args:
                if arg_name == 'VERSION_1_4_0':
                    args_values.append('true')  # 为 VERSION_1_4_0 提供值
                elif arg_name == 'hostname':
                    args_values.append(hostname)
                elif arg_name == 'port':
                    args_values.append(str(port))
                elif arg_name == 'domain':
                    args_values.append('')  # 如果没有域名，可以发送空字符串
                elif arg_name == 'username':
                    args_values.append(username)
                elif arg_name == 'password':
                    args_values.append(password)
                elif arg_name == 'ignore-cert':
                    args_values.append('true')
                elif arg_name == 'security':
                    args_values.append('any')  # 自动协商安全模式
                elif arg_name == 'width':
                    args_values.append('1024')  # 默认宽度
                elif arg_name == 'height':
                    args_values.append('768')   # 默认高度
                elif arg_name == 'dpi':
                    args_values.append('96')    # 默认 DPI
                elif arg_name == 'color-depth':
                    args_values.append('32')    # 默认颜色深度
                elif arg_name == 'disable-audio':
                    args_values.append('true')  # 禁用音频
                elif arg_name == 'enable-wallpaper':
                    args_values.append('false') # 禁用壁纸
                elif arg_name == 'enable-theming':
                    args_values.append('false') # 禁用主题
                elif arg_name == 'enable-font-smoothing':
                    args_values.append('false') # 禁用字体平滑
                elif arg_name == 'enable-full-window-drag':
                    args_values.append('false') # 禁用全窗口拖动
                elif arg_name == 'enable-desktop-composition':
                    args_values.append('false') # 禁用桌面合成
                elif arg_name == 'enable-menu-animations':
                    args_values.append('false') # 禁用菜单动画
                elif arg_name == 'console':
                    args_values.append('false') # 禁用控制台
                elif arg_name == 'console-audio':
                    args_values.append('false') # 禁用控制台音频
                elif arg_name == 'disable-auth':
                    args_values.append('false')  # 禁用身份验证
                else:
                    args_values.append('')  # 对于未知的参数，发送空字符串

            # 打印参数名称和值的对应关系，用于调试
            print("Parameter mapping:")
            for name, value in zip(requested_args, args_values):
                print(f"  {name}: {value}")

            # 4. 发送 'connect' 指令，提供参数值
            self._send_instruction('connect', args_values)

            # 5. 读取服务器的响应
            response = self._read_instruction()
            print(f"Received response: {response}")
            if response[0] != "ready":
                raise ConnectionError(f"Guacamole server not ready: {response}")

            connection_id = response[1]
            return connection_id

        except Exception as e:
            print(f"Error connecting to guacd: {e}")
            self.disconnect()

    def _send_instruction(self, opcode, args):
        """发送指令到 guacd"""
        instruction = f"{len(opcode)}.{opcode},"
        instruction += ",".join([f"{len(arg)}.{arg}" for arg in args])
        instruction += ";"
        self.sock.sendall(instruction.encode('utf-8'))

    def _read_instruction(self):
        """读取并解析 guacamole instruction"""
        buffer = ''
        while True:
            data = self.sock.recv(4096).decode('utf-8')
            if not data:
                break
            buffer += data
            if ';' in buffer:
                break

        instruction_str = buffer.split(';')[0]
        parts = instruction_str.split(',')

        args = []
        for part in parts:
            if not part:
                continue
            length_str, value = part.split('.', 1)
            length = int(length_str)
            args.append(value[:length])

        return args

    def disconnect(self):
        """断开与 guacd 的连接"""
        if self.connected:
            self.sock.close()
            self.connected = False

    def send(self, data):
        """向 guacd 发送数据"""
        if self.connected:
            self.sock.sendall(data)

    def receive(self):
        """从 guacd 接收数据"""
        if self.connected:
            return self.sock.recv(4096)
        return None