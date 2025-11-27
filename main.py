import asyncio
import io
import os.path
import random

import PIL.Image
import qrcode.main
from pyzbar import pyzbar
from qqmusic_api import Credential
from qqmusic_api.login import QR, QRLoginType, get_qrcode, check_qrcode, QRCodeLoginEvents, check_expired, \
    refresh_cookies
from qqmusic_api.songlist import create, get_songlist, del_songs, add_songs
from qqmusic_api.user import get_euin, get_fav_song, get_created_songlist


async def get_and_print_login_qr(login_type: QRLoginType) -> QR:
    """
    获取登陆二维码并在控制台中打印
    :param login_type: 登陆类型，qq或者微信
    :return: 获取到的api库QR对象
    """

    # 调用api获取二维码图片二进制数据
    api_qr: QR = await get_qrcode(login_type)
    # 读取为图片
    img = PIL.Image.open(io.BytesIO(api_qr.data))

    # 解码二维码，获取其中的url
    qr_content = pyzbar.decode(img)
    login_url = qr_content[0].data.decode("utf-8")

    # 使用url，生成新的二维码，在控制台打印输出
    ascii_qr = qrcode.main.QRCode()
    ascii_qr.add_data(login_url)
    # ascii_qr.print_ascii(tty=True, invert=True)
    ascii_qr.print_ascii()

    return api_qr


async def do_api_qr_login(api_login_type: QRLoginType) -> Credential | None:
    """
    获取登陆二维码并在控制台打印，轮询检查用户扫码登陆状态，可能会抛出登陆失败异常
    :return: 如果登陆成功，返回api的认证信息对象；否则返回NULL
    """
    while True:
        # 获取、打印二维码
        api_qr: QR = await get_and_print_login_qr(api_login_type)
        # 轮询检查
        while True:
            event, credential = await check_qrcode(api_qr)
            match event:
                case QRCodeLoginEvents.DONE:
                    # 扫码登陆成功，返回认证信息
                    return credential
                case QRCodeLoginEvents.TIMEOUT:
                    print("二维码已过期")
                    break
                case _:
                    await asyncio.sleep(2)
        # 通常是二维码到期
        return None


async def get_fav_song_count(euid: str, credential: Credential) -> int:
    """
    获取“我喜欢”歌曲总数
    """
    fav_songs = await get_fav_song(euid, -1, 0, credential=credential)
    return fav_songs["total_song_num"]


async def get_fav_song_info(euid: str, credential: Credential, song_index: int):
    """
    获取“我喜欢”歌曲列表中，指定index位置歌曲的信息
    :param euid:
    :param credential:
    :param song_index: 歌曲index，注意是从1开始，使用0也会返回1的内容
    :return: 歌曲信息dict，通常使用以下key：id, name, album/name
    """
    fav_song = await get_fav_song(euid, song_index, 1, credential=credential)
    # TODO：考虑拼装为歌曲id、歌名、专辑等内容的易用对象
    return fav_song["songlist"][0]


async def find_exist_random_playlist(credential: Credential) -> dict | None:
    """
    查找先前生成的"_RandomPlaylist_"歌单
    :param credential:
    :return: 如果找到了，返回其歌单信息；否则返回None
    """

    # 返回的列表包含"喜欢"
    all_playlists = await get_created_songlist(str(credential.musicid), credential=credential)

    # 遍历比较其中的"dirName"
    for playlist in all_playlists:
        if playlist["dirName"] == "_RandomPlaylist_":
            return playlist

    # 找不到，返回-1
    return None


async def test():
    credential = None

    if os.path.exists("credentials.json"):
        with open("credentials.json", "r") as f:
            credential = Credential.from_cookies_str(f.read())

    if credential is None or await check_expired(credential):
        credential = await do_api_qr_login(QRLoginType.QQ)
        if credential is None:
            exit(-1)

    euid = await get_euin(credential.musicid)
    print(f"euid: {euid}")

    playlist = await find_exist_random_playlist(credential)
    if playlist is None:
        playlist = await create("_RandomPlaylist_", credential=credential)

    old_content = await get_songlist(playlist["tid"], playlist["dirId"])
    old_ids = []
    for song in old_content:
        old_ids.append(song["id"])

    await del_songs(playlist["dirId"], old_ids, credential=credential)

    total_fav = await get_fav_song_count(euid, credential=credential)
    new_ids = []
    for index in random.choices(range(1, total_fav + 1), k=50):
        fav_song_info = await get_fav_song_info(euid, credential, index)
        new_ids.append(fav_song_info["id"])

    await add_songs(playlist["dirId"], new_ids, credential=credential)

    await refresh_cookies(credential)
    with open("credentials.json", "w") as f:
        f.write(credential.as_json())


if __name__ == "__main__":
    asyncio.run(test())
