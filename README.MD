# RandomPlaylistGenerator

简称RPG。

从QQ音乐的“喜欢”(红心)音乐列表随机抽取音乐生成歌单。

主要解决某些抽象[车机](https://flymeauto.com/)上的QQ音乐客户端只能随机缓存的前十几首音乐，
以及QQ音乐的随机功能本身就很拉垮。

# Roadmap

- [ ] 实现运行参数配置
- [x] 支持在同一歌单上清空歌曲重新生成添加，避免“恢复歌单”页面出现太多内容
- [x] 保存随机历史，避免多次生成重复出现
- [x] 补充必要的[QQMusicApi](https://github.com/L-1124/QQMusicApi)库文档
