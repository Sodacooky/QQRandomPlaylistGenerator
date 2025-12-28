from qqmusic_api.login import QRLoginType

from login_manager import LoginManager
from random_history import RandomHistory
from random_picker import RandomPicker
from random_songlist import RandomSonglist


def test():
    login_manager = LoginManager()
    if not login_manager.load_credential_file():
        login_manager.do_qr_login(QRLoginType.QQ)
        login_manager.save_credential_file()
    print(f"已登录EUID: {login_manager.get_euid()}")

    random_picker = RandomPicker(login_manager, RandomHistory())
    random_ids = random_picker.pick(100)

    random_songlist = RandomSonglist(login_manager)
    random_songlist.update(random_ids)
    print("更新完成")


if __name__ == "__main__":
    test()
