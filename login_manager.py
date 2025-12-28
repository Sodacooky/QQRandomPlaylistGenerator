import asyncio
import io
import os
from time import sleep

from qqmusic_api import Credential
from qqmusic_api.login import QRLoginType, get_qrcode, QR, check_expired, refresh_cookies, check_qrcode, \
    QRCodeLoginEvents
from qqmusic_api.user import get_euin


class LoginManager:
    """
    管理登陆状态
    """

    # 凭证文件名
    __CREDENTIAL_FILENAME = "credential.json"

    # 当前登陆的凭证
    __credential: Credential | None = None

    # 缓存的EUID
    __euid_cached: str | None = None

    def __init__(self):
        pass

    def do_qr_login(self, api_login_type: QRLoginType) -> bool:
        """
        获取登陆二维码并在控制台打印，轮询检查用户扫码登陆状态，可能会抛出登陆失败异常
        :return: 登陆是否成功
        """
        # 检查是否已经登陆，如果已经登陆则什么都不做
        if self.__credential is not None:
            return True
        # 二维码登陆循环
        while True:
            # 获取、打印二维码
            api_qr: QR = self.__get_and_print_login_qr(api_login_type)
            # 轮询检查
            while True:
                event, credential = asyncio.run(check_qrcode(api_qr))
                match event:
                    case QRCodeLoginEvents.DONE:
                        # 扫码登陆成功
                        self.__credential = credential
                        return True
                    case QRCodeLoginEvents.TIMEOUT:
                        # 二维码过期，回到二维码生成
                        print("二维码已过期")
                        break
                    case _:
                        # 其他情况，等待两秒再检查状态
                        sleep(2)
        # 只能通过终止运行退出

    def get_credential(self) -> Credential | None:
        """
        :return: 当前登陆的凭证Credential，或者未登陆返回None
        """
        return self.__credential

    def get_euid(self) -> str:
        """
        通过credential中的musicid获取euid
        :return: 用户euid
        """
        if self.__euid_cached is None:
            self.__euid_cached = asyncio.run(get_euin(self.__credential.musicid))
        return self.__euid_cached

    def save_credential_file(self, credential_file_path: str = None):
        """
        保存凭证文件到指定位置
        :param credential_file_path: 保存凭证文件路径，如果传入None则尝试使用运行路径下的credential.json
        """
        if credential_file_path is None:
            credential_file_path = self.__CREDENTIAL_FILENAME
        with open(credential_file_path, "w") as f:
            f.write(self.__credential.as_json())

    def load_credential_file(self, credential_file_path: str = None) -> bool:
        """
        加载凭证文件尝试登陆
        :param credential_file_path: 凭证文件路径，如果传入None则尝试使用运行路径下的credential.json
        :return: 是否使用加载的凭证文件登陆成功
        """

        # 尝试读取指定的credential.json文件
        if credential_file_path is not None and os.path.exists(credential_file_path):
            with open(credential_file_path, "r") as credential_file:
                self.__credential = Credential.from_cookies_str(credential_file.read())
        # 尝试读取运行目录下的credential.json文件
        elif os.path.exists(self.__CREDENTIAL_FILENAME):
            with open(self.__CREDENTIAL_FILENAME, "r") as credential_file:
                try:
                    self.__credential = Credential.from_cookies_str(credential_file.read())
                except Exception as e:
                    print("加载凭证文件失败，忽略")
        # 无法读取到保存的凭证，为未登录状态
        else:
            self.__credential = None

        # 验证凭证是否有效，如果无效也需要重新登陆
        if self.__credential is not None:
            if asyncio.run(check_expired(self.__credential)):
                # 凭证无效，恢复为未登录状态
                self.__credential = None
                print("提供的凭证已过期或无效")
                return False
            else:
                # 凭证有效，刷新
                asyncio.run(refresh_cookies(self.__credential))
                print("成功使用提供的凭证文件登陆")
                return True
        # 没有凭证，未登录
        return False

    @staticmethod
    def __get_and_print_login_qr(login_type: QRLoginType) -> QR:
        """
        获取登陆二维码并在控制台中打印
        :param login_type: 登陆类型
        :return: 获取到的qqmusic_api库QR对象
        """
        import qrcode.main
        from pyzbar import pyzbar
        from PIL import Image

        # 调用api获取二维码图片二进制数据
        api_qr: QR = asyncio.run(get_qrcode(login_type))
        # 读取为图片
        img = Image.open(io.BytesIO(api_qr.data))

        # 解码二维码，获取其中的url
        qr_content = pyzbar.decode(img)
        login_url = qr_content[0].data.decode("utf-8")

        # 使用url，生成新的二维码，在控制台打印输出
        ascii_qr = qrcode.main.QRCode()
        ascii_qr.add_data(login_url)
        # ascii_qr.print_ascii(tty=True, invert=True)
        ascii_qr.print_ascii()

        return api_qr
