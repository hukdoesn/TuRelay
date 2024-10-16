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
            # 调试日志，打印连接参数，确保传递的参数正确
            print(f"Connecting to guacd with the following parameters:")
            print(f"Protocol: {protocol}, Hostname: {hostname}, Port: {port}, Username: {username}")

            # 创建到 guacd 的 socket 连接
            self.sock = socket.create_connection((self.guacd_host, self.guacd_port))
            self.connected = True

            # 发送 'select' 指令，选择 RDP 协议
            self._send_instruction('select', [protocol])

            # 接收服务器请求的参数列表
            instruction = self._read_instruction()
            if instruction[0] != 'args':
                raise Exception(f"Expected 'args' instruction, but got '{instruction[0]}'")

            requested_args = instruction[1:]
            print(f"Server requested args: {requested_args}")

            # 根据服务器请求的参数列表，按顺序提供参数值
            args_values = self._build_args_values(requested_args, hostname, port, username, password)
            
            # 打印参数名称和值，调试用
            print("Parameter mapping:")
            for name, value in zip(requested_args, args_values):
                print(f"  {name}: {value}")

            # 发送 'connect' 指令，传递所有参数
            self._send_instruction('connect', args_values)

            # 读取服务器响应，检查是否准备好
            response = self._read_instruction()
            print(f"Received response: {response}")
            if response[0] != "ready":
                raise ConnectionError(f"Guacamole server not ready: {response}")

            # 返回连接 ID
            connection_id = response[1]
            return connection_id

        except Exception as e:
            print(f"Error connecting to guacd: {e}")
            self.disconnect()

    def _build_args_values(self, requested_args, hostname, port, username, password):
        """构建参数值列表，确保传递有效的参数"""
        args_values = []
        for arg_name in requested_args:
            if arg_name == 'VERSION_1_4_0':
                args_values.append('true')  # 版本兼容
            elif arg_name == 'hostname':
                args_values.append(hostname)
            elif arg_name == 'port':
                args_values.append(str(port))
            elif arg_name == 'domain':
                args_values.append('')  # 空域名
            elif arg_name == 'username':
                args_values.append(username)
            elif arg_name == 'password':
                args_values.append(password)
            elif arg_name == 'ignore-cert':
                args_values.append('true')  # 忽略证书验证
            elif arg_name == 'security':
                args_values.append('any')  # 自动协商安全模式
            elif arg_name == 'width':
                args_values.append('1024')  # 确保提供有效的宽度值
            elif arg_name == 'height':
                args_values.append('768')   # 确保提供有效的高度值
            elif arg_name == 'dpi':
                args_values.append('96')    # DPI 默认为 96
            elif arg_name == 'color-depth':
                args_values.append('32')    # 32 位颜色深度
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
            else:
                args_values.append('')  # 未知参数发送空字符串
        return args_values

    def _send_instruction(self, opcode, args):
        """发送指令到 guacd"""
        instruction = f"{len(opcode)}.{opcode},"
        instruction += ",".join([f"{len(arg)}.{arg}" for arg in args])
        instruction += ";"
        self.sock.sendall(instruction.encode('utf-8'))

    def _read_instruction(self):
        """读取并解析 guacd 指令"""
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
