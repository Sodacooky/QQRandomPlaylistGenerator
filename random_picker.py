import asyncio
import random

from qqmusic_api.user import get_fav_song

from login_manager import LoginManager
from random_history import RandomHistory


class RandomPicker:
    """
    生成随机音乐歌单
    """

    def __init__(self, login_manager: LoginManager, random_history: RandomHistory):
        self.__login_manager = login_manager
        self.__random_history = random_history

    def pick(self, count: int) -> list[int]:
        """
        在排除了历史已随机歌曲的情况下，从“喜欢”歌曲中随机抽取若干，
        抽取完成后本地抽取结果会储存到历史中。

        当要抽取的数量大于剩余歌曲数量时，会清空历史随机记录。

        :param count: 要抽取的数量
        :return: 抽中的ID列表
        """
        # 获取已随机的歌曲id集合
        history_set: set = self.__random_history.get_history()
        # 获取全部喜欢歌曲集合
        all_set: set = set(self.__fetch_all_fav_song_ids())
        # 计算差集
        available_set: set = all_set - history_set

        # 判断是否剩余歌曲数量不足，如果是则清除历史，并从全部歌曲合集中抽取
        if count > len(available_set):
            self.__random_history.clear_history()
            available_set = all_set
            print("排除历史已随机歌曲后剩余歌曲数量不足，已重置历史")

        # 抽取并记录
        picked = random.sample(list(available_set), count)
        self.__random_history.add_history(picked)
        # 返回
        return picked

    def __fetch_fav_song_count(self) -> int:
        """
        :return: “喜欢”歌曲数量
        """
        euid = self.__login_manager.get_euid()
        credential = self.__login_manager.get_credential()
        fav_songs = asyncio.run(get_fav_song(euid, -1, 0, credential=credential))
        return fav_songs["total_song_num"]

    def __fetch_all_fav_song_ids(self):
        """
        获取所有“喜欢”歌曲的ID
        :return: 用户所有“喜欢”歌曲的ID列表
        """
        # 获取喜欢歌曲数量，用于计算分页
        fav_song_count = self.__fetch_fav_song_count()
        print(f"“喜欢”歌曲数量: {fav_song_count}")

        # get_fav_song的响应其实很快，即使一次性获取大量歌曲，因此我们按照1页1000首进行切割
        page_count: int = (fav_song_count // 1000) + 1
        page_size = 1000
        euid = self.__login_manager.get_euid()
        credential = self.__login_manager.get_credential()

        # 同步循环获取
        print("正在获取“喜欢”歌曲列表...")
        result_ids: list = []
        for page_index in range(page_count):
            fav_songs_response = asyncio.run(get_fav_song(euid, page_index + 1, page_size, credential=credential))
            # 遍历song_list列表
            for song in fav_songs_response["songlist"]:
                # 获取id
                result_ids.append(song["id"])
                # TODO：其实可以考虑把歌名也存下来，便于生成结果展示？
            print(f"已获取 {page_index + 1}/{page_count} 页")

        return result_ids
