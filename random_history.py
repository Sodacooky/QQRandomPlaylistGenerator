import sqlite3
import time


class RandomHistory:
    """
    使用sqlite储存随机过的音乐ID和时间
    """

    # 创建表SQL指令
    __CREATE_TABLE_SQL = ("""
                          CREATE TABLE IF NOT EXISTS "history"
                          (
                              add_time
                                  integer
                                  not
                                      null,
                              song_id
                                  integer
                                  not
                                      null,
                              constraint
                                  history_pk
                                  primary
                                      key
                                      (
                                       add_time,
                                       song_id
                                          )
                          )
                          """)

    def __init__(self, db_path: str = "history.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # 如果表不存在，进行创建
        self.cursor.execute(self.__CREATE_TABLE_SQL)

    def get_history(self) -> set:
        """
        :return: 历史随机过的音乐id列表
        """
        return set(self.cursor.execute("select song_id from main.history").fetchall())

    def add_history(self, song_id_list: list[int]) -> None:
        """
        将音乐id列表，以当前时间添加到历史随机过的音乐中
        :param song_id_list: 音乐id列表
        """
        add_time = int(time.time())
        self.cursor.executemany("insert into main.history values (?, ?)",
                                [(add_time, song_id) for song_id in song_id_list])
        self.conn.commit()

    def clear_history(self) -> None:
        """
        清空历史随机过的音乐id
        """
        self.cursor.execute("delete from main.history")
        self.conn.commit()
