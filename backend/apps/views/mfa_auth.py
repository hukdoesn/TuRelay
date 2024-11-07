import pyotp
import qrcode
import base64
from io import BytesIO

class MFAUtil:
    @staticmethod
    def generate_secret():
        """生成OTP密钥"""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(username, secret_key, issuer_name="TuRelay"):
        """
        生成二维码
        :param username: 用户名
        :param secret_key: OTP密钥
        :param issuer_name: 发行方名称
        :return: base64编码的二维码图片
        """
        # 创建OTP URI
        totp = pyotp.TOTP(secret_key)
        provisioning_uri = totp.provisioning_uri(username, issuer_name=issuer_name)

        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # 创建二维码图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    @staticmethod
    def verify_otp(secret_key, otp_code):
        """
        验证OTP代码
        :param secret_key: OTP密钥
        :param otp_code: 用户提供的OTP代码
        :return: bool
        """
        if not secret_key or not otp_code:
            return False
        
        totp = pyotp.TOTP(secret_key)
        return totp.verify(otp_code) 