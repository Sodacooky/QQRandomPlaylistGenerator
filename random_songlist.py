import asyncio
import random

from qqmusic_api.songlist import create, get_songlist, del_songs, add_songs
from qqmusic_api.user import get_created_songlist

from login_manager import LoginManager


class RandomSonglist:
    """
    随机音乐歌单相关
    """

    # 随机音乐歌单的tid/songlist_id
    tid: int = -1

    # 随机音乐歌单的dirId
    dirId: int = -1

    def __init__(self, login_manager: LoginManager, name: str = "_RandomPlaylist_"):
        """
        :param login_manager: 登陆信息
        :param name: 随机歌单名称，默认为"_RandomPlaylist_"
        """
        self.__login_manager = login_manager
        self.__name = name
        # 查找已有随机歌单，如果没有找到则创建
        if not self.__find_random_list():
            self.__create_random_list()

    def update(self, song_ids: list[int]):
        """
        清空歌单原有歌曲，将新歌曲加入到歌单
        :param song_ids: 新的歌曲ID列表
        """
        # TODO: 没有检查歌单无效的情况
        credential = self.__login_manager.get_credential()
        # 获取歌单原有歌曲，进行删除
        asyncio.run(del_songs(self.dirId, self.__fetch_current_song_ids(), credential=credential))
        # 对ID列表再次进行打乱，避免顺序与时间顺序相关
        random.shuffle(song_ids)
        # 添加到歌单
        asyncio.run(add_songs(self.dirId, song_ids, credential=credential))

    def __find_random_list(self) -> bool:
        """
        查找随机歌单，如果找到了则更新self.tid和self.dirId
        :return: 是否找到
        """
        credential = self.__login_manager.get_credential()
        all_songlist = asyncio.run(get_created_songlist(str(credential.musicid), credential=credential))
        for songlist in all_songlist:
            if songlist["dirName"] == self.__name:
                self.tid = songlist["tid"]
                self.dirId = songlist["dirId"]
                return True
        return False

    def __create_random_list(self):
        """
        创建新的随机歌单，并更新self.tid和self.dirId
        """
        songlist = asyncio.run(create(self.__name, self.__login_manager.get_credential()))
        self.tid = songlist["tid"]
        self.dirId = songlist["dirId"]

    def __fetch_current_song_ids(self) -> list[int]:
        """
        获取歌单当前的歌曲ID列表，通常用于删除歌曲
        :return: 歌单中现有歌曲ID列表
        """
        ids: list[int] = []
        songlist = asyncio.run(get_songlist(self.tid, self.dirId))
        for song in songlist:
            ids.append(song["id"])
        return ids
