![maven](https://img.shields.io/badge/python-3.9%2B-blue)
![maven](https://img.shields.io/badge/nonebot-2.0.0-yellow)
![maven](https://img.shields.io/badge/go--cqhttp-1.0.0-red)

# 桃桃Bot  
此项目是基于 [Nonebot2](https://github.com/nonebot/nonebot2) 和 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的QQ群聊娱乐机器人  
借(chao)鉴(xi)了大佬们的代码，实现了一些对群友的娱乐功能和实用功能（大概  


# Nonebot2
<img style="height: 100px;width: 100px;" src="https://camo.githubusercontent.com/0ef71e86056da694c540790aa4a4e314396884d6c4fdb95362a7538b27a1b034/68747470733a2f2f76322e6e6f6e65626f742e6465762f6c6f676f2e706e67">

非常 [ **[NICE](https://github.com/nonebot/nonebot2)** ] 的OneBot框架


## 声明
此项目仅用于学习交流，不可商用以及非法用途  


## 功能列表
### PicSearch  搜图
抄自 [NekoAria佬](https://github.com/NekoAria) 的 [YetAnotherPicSearch](https://github.com/NekoAria/YetAnotherPicSearch)  
将原插件的 **搜图** 改为 **搜图#** ，增加了隐蔽性，防止误触（x  
需要在 `.env.dev` 文件中添加saucenao的apikey：  
```
SAUCENAO_API_KEY=xxx
```
除此之外请参考原插件 [▶使用方法️️](https://github.com/NekoAria/YetAnotherPicSearch/blob/main/docs/%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md)


### anti_abuse  嘴臭屏蔽
检测到有用户@机器人并嘴臭时将其临时屏蔽(bot重启后失效)  
当bot为群管理时会请对方喝昏睡红茶


### anti_flash  反闪照
抄自 [KafCoppelia佬](https://github.com/MinatoAquaCrews) 的 [AntiFlash](https://github.com/MinatoAquaCrews/nonebot_plugin_antiflash)  

<details>
  <summary>使用方法(点击展开)</summary>
  
.  
在`.env.dev`内设置：

```python
ANTI_FLASH_ON=true                          # 全局开关
ANTI_FLASH_GROUP=["123456789", "987654321"] # 默认开启的群聊，但可通过指令开关
ANTI_FLASH_PATH="your-path-to-config.json"  # 配置文件路径，默认同插件代码路径
```

`ANTI_FLASH_GROUP`会在每次初始化时写入配置文件，在群组启用反闪照，可通过指令更改。  
  
**修改** 配置文件即读即改，可后台修改。  
  
**功能:**
1. 全局开关**仅超管**配置，不支持指令修改全局开关；  
2. 各群聊均配置开关，需**管理员及超管权限**进行修改；  
  
**命令:**  
开启/启用/禁用反闪照

</details>


### anti_recall  反撤回
移植自 [摸佬](https://github.com/Kyomotoi) 的 [ATRI](https://github.com/Kyomotoi/ATRI)  
将检测到的撤回消息转发给超级用户


### bhbdm  不会百度么？
发送 `/百度搜索` 加 `内容` 返回直达链接  
<img style="height: 150px; width: 430px;" src="https://iili.io/6vMyOP.jpg">


### caiyun_ai  AI续写
抄自 [wq佬](https://github.com/MeetWq) 的 [caiyunai](https://github.com/noneplugin/nonebot-plugin-caiyunai)  

<details>
  <summary>使用方法(点击展开)</summary>
  
.  
**配置:**

需要在 `.env.dev` 文件中添加彩云小梦apikey：

```
CAIYUNAI_APIKEY=xxx
```

apikey获取：

前往 http://if.caiyunai.com/dream 注册彩云小梦用户；

注册完成后，F12打开开发者工具；

在控制台中输入 `alert(localStorage.cy_dream_user)` ，弹出窗口中的 uid 即为 apikey；

或者进行一次续写，在 Network 中查看 novel_ai 请求，Payload 中的 uid 项即为 apikey。


**使用:**  
```
@机器人 续写/彩云小梦 xxx
```

</details>

### echo  说
**使用方法:**  
`@机器人` 并加上 **全角冒号** `：` 发送你想让机器人说的话
```
@桃桃酱 ：xxxxx
```
为防止恶意用户滥用导致封号，限制仅超级用户可用


### eventdone  好友添加事件处理
抄自 [PadorFelice佬](https://github.com/PadorFelice) 的 [eventdone](https://github.com/PadorFelice/nonebot_plugin_eventdone)  
**使用方法:**  
私聊发送 `同意` 加申请人qq号
```
同意 xxxxxxxxx
```


### fake_msg  伪造合并转发消息
移植自 [摸佬](https://github.com/Kyomotoi) 的 [ATRI](https://github.com/Kyomotoi/ATRI)  
**使用方法:**  
```
/fakemsg
qq号-昵称-消息内容
```
示例:  
```
/fakemsg
123456789-桃桃酱-不可以色色
987654321-路人甲-我就要色色
```

### look_like  你看我像人吗
**使用方法:**  
`@机器人` 发送 `你看我像`  
示例:  
```
@桃桃酱 你看我像人吗？
```


### mockingbird  让bot发语音
抄自 [白毛佬](https://github.com/AkashiCoin) 的 [mockingbird](https://github.com/AkashiCoin/nonebot_plugin_mockingbird)  
**使用方法:**  
```
@Bot 说 [你想要bot说的话]
```
配置不够的设备使用该功能容易死机，所以修改了权限限制仅超级用户可用。  
如果需要开放给所有用户使用的话，请将`plugins/mockingbird/__init__.py`第78行的`permission=SUPERUSER,`删掉

<details>
  <summary>其他操作(点击展开)</summary>
  
.  
```
显示模型 # 显示出可供修改的模型
# 修改指令
修改模型 [序号]\[模型名称]
重载模型 进行模型重载(并没有什么卵用，或许以后内存泄漏解决会有用？)
调整/修改精度 修改语音合成精度
调整/修改句长 修改语音合成最大句长
更新模型 更新模型列表
```

</details>


### blacklist  黑名单
  

<details>
  <summary>使用方法(点击展开)</summary>

.  

拉黑:  
```
拉黑用户 qq qq1 qq2  
拉黑群 qq qq1 qq2  
```
  
解禁:  
```
解禁用户 qq qq1 qq2  
解禁群 qq qq1 qq2  
```
  
查看黑名单:  
```
查看用户黑名单  
查看群聊黑名单  
```
群内发送 **`/静默`**, **`/响应`** 可快捷拉黑/解禁当前群聊  

</details>


### rss  订阅
抄自 [Quan666](https://github.com/Quan666) 的 [ELF_RSS](https://github.com/Quan666/ELF_RSS)  
**使用方法:** [▶传送门](https://github.com/Quan666/ELF_RSS/blob/2.0/docs/2.0%20%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md)  


### simplemusic  点歌
抄自 [wq佬](https://github.com/MeetWq) 的 [SimpleMusic](https://github.com/noneplugin/nonebot-plugin-simplemusic)  
**使用方法:**  
```
@机器人 点歌/qq点歌/网易点歌/酷我点歌/酷狗点歌/咪咕点歌/b站点歌 + 关键词
```
默认为qq点歌


### smart_reply  AI聊天
抄自 [Special-Week佬](https://github.com/Special-Week) 的 [SmartReply](https://github.com/Special-Week/nonebot_plugin_smart_reply)  
**使用方法:**  
`@机器人` 发送你想对机器人说的骚话


### status  

发送 `/ping` 测试bot应答  
发送 `/status` 查看bot设备状态  
超级用户使用


### tarot  抽塔罗牌
**使用方法:**  
```
@机器人 抽塔罗牌
```


### wordbank2  你问我答
抄自 [kexue佬](https://github.com/kexue-z) 的 [wordbank2](https://github.com/kexue-z/nonebot-plugin-word-bank2)
**使用方法:** [▶传送门](https://github.com/kexue-z/nonebot-plugin-word-bank2#%E5%BC%80%E5%A7%8B%E4%BD%BF%E7%94%A8)


### withdraw  撤回
回复机器人的消息发送 `撤回`


## 部署方式
...

