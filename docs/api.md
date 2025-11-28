# API响应数据参考

因为[QQMusicApi](https://github.com/L-1124/QQMusicApi)库的文档没有给出响应内容封装或说明，
因此只能自己测试发送请求打印响应的内容分析。

此处只记录用到的API的响应结果的必要内容，即省略无关结构。

返回的内容应该是JSON，被转成了dict对象，直接使用即可。

## user

### get_fav_song

获取收藏的歌曲的信息，也可以用于获取收藏的歌曲数量。

> 收藏歌曲这里指的是“喜欢”或者“红心”的音乐

响应：

```json5
{
  //收藏歌曲总数，总是返回，因此可以用“获取-1页的0首歌曲”请求来获取
  'total_song_num': 893,
  //返回的歌单大小，通常就是调用api传入的大小
  'songlist_size': 1,
  //获取的指定页的收藏歌曲列表
  'songlist': [
    //每个元素都是歌曲信息
    {
      //歌曲ID
      'id': 1145141919810,
      //歌名
      'name': 'Element of SPADA',
      //所属专辑信息，可能会没有？
      'album': {
        //专辑ID
        'id': 12345678,
        'name': 'follow slowly',
        'title': 'follow slowly',
        //name和title参考singer中的描述
      },
      //歌手列表
      'singer': [
        //每个元素都是歌手信息
        {
          'name': '猫叉Master',
          'title': '猫叉Master (さとう なおゆき)',
          //优先使用name展示，title是歌手详细页显示的
        }
      ]
    }
  ]
}
```

### get_created_songlist

获取用户创建的歌单。

> 需要注意，“喜欢”即红心音乐也会作为歌单出现在响应的列表中

响应：

```json5
//响应内容是一个数组，每个元素都是歌单信息对象
[
  {
    //歌单的id，api库中会写作参数名songlist_id
    'tid': 7950345341,
    //也是歌单的id，应该是用户域下的，api库中参数名通常就是dirId
    'dirId': 2,
    //歌单名称
    'dirName': 'MyBestFavo',
    //歌单中的歌曲数量
    'songNum': 29,
    //创建时间，unix epoch时间，单位为秒
    'createTime': 1617380805,
  }
]
```

### get_homepage

获取用户主页信息。

内容很多很杂，目前项目中只用到获取用户昵称。

响应：

```json5
{
  'Info': {
    'BaseInfo': {
      //用户昵称
      'Name': 'Sodacooky',
    }
  }
}
```

## songlist

#### get_songlist

获取歌单中所有歌曲列表。

要求同时传入`songlist_id`(即上文提到的`tid`)和`dirId`，不知道是不是确实都必须，实测不给`songlist_id`会出错。

响应：

```json5
//返回的数组中，每一个都是歌曲信息，与get_fav_song中的相同
[
  {
    //歌曲信息
  }
]
```

> 具体歌曲信息结构见[get_fav_song部分](#get_fav_song)

#### create

添加歌单, 重名会在名称后面添加时间戳。

响应：

```json5
//刚刚创建的歌单的信息，与user.get_created_songlist响应内容类似
{
  //歌单ID，用户域下
  'dirId': 1,
  //歌单名称
  'dirName': 'haha',
  //歌单ID
  'tid': 9619098238,
  //更新时间，unix epoch秒
  'updateTime': 1764166821
}

```