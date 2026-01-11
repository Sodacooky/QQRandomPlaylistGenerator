import asyncio
import io
import os
from time import sleep

from qqmusic_api import Credential
from qqmusic_api.login import QRLoginType, get_qrcode, QR, refresh_cookies, check_qrcode, \
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
        :return: 当前登陆的凭证Credential，或者未加载凭证文件时返回None
        """
        return self.__credential

    def get_euid(self) -> str | None:
        """
        通过credential中的musicid获取euid
        :return: 用户euid，或者未加载凭证文件时返回None
        """
        if self.__credential is None:
            return None
        if self.__euid_cached is None:
            self.__euid_cached = asyncio.run(get_euin(self.__credential.musicid))
        return self.__euid_cached

    def refresh(self) -> bool:
        """
        刷新登陆凭证。
        应该可以在登陆失效时通过credential中的refresh_key和refresh_token更新为有效登陆凭证。
        :return: 是否刷新成功，也可以用作凭证文件是否有效的依据
        """
        if self.__credential is None:
            raise RuntimeError("尝试在未加载Credential文件时进行refresh操作")
        print("正在refresh登陆凭证文件")
        return asyncio.run(refresh_cookies(self.__credential))

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
        加载凭证文件
        :param credential_file_path: 凭证文件路径，如果传入None则尝试使用运行路径下的credential.json
        :return: 是否成功加载的凭证文件
        """
        # 当没有指定凭证文件路径时，从默认路径读取
        if credential_file_path is None:
            credential_file_path = self.__CREDENTIAL_FILENAME

        # 尝试读取credential.json文件
        if os.path.exists(credential_file_path):
            with open(credential_file_path, "r") as credential_file:
                try:
                    self.__credential = Credential.from_cookies_str(credential_file.read())
                    print(f"已读取凭证文件{os.path.abspath(credential_file_path)}")
                    return True
                except Exception as e:
                    print("加载凭证文件失败：", e)
                    return False
        else:
            print(f"路径 {os.path.abspath(credential_file_path)} 不存在")
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
