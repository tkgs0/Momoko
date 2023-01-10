
# 桃桃Bot  
此项目是基于 [Nonebot2](https://github.com/nonebot/nonebot2) 和 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的QQ群聊娱乐机器人  
借(chao)鉴(xi)了大佬们的代码，实现了一些对群友的娱乐功能和实用功能（大概  

<div>

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/tkgs0/Momoko.svg" alt="license">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
</a>
<a href="https://https://v2.nonebot.dev">
    <img src="https://img.shields.io/badge/nonebot-2.0.0-red.svg" alt="NoneBot">
</a>
<a href="https://onebot.adapters.nonebot.dev">
    <img src="https://img.shields.io/badge/onebot-v11-black.svg" alt="OneBot">
</a>
<a href="https://github.com/Mrs4s/go-cqhttp">
    <img src="https://img.shields.io/badge/gocq-1.0.0-blueviolet.svg" alt="go-cqhttp">
</a>

</div>


# NoneBot2

<div>
<a href="https://v2.nonebot.dev">
    <img style="height: 150px;width: 150px;" src="https://camo.githubusercontent.com/0ef71e86056da694c540790aa4a4e314396884d6c4fdb95362a7538b27a1b034/68747470733a2f2f76322e6e6f6e65626f742e6465762f6c6f676f2e706e67" alt="NoneBot">
</a>

非常 [ **[NICE](https://github.com/nonebot/nonebot2)** ] 的Bot框架

</div>


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
**被动插件**  
检测到有用户@机器人并嘴臭时将其临时屏蔽(bot重启后失效)  
当bot为群管理时会请对方喝昏睡红茶  
饮用了昏睡红茶的用户不会进临时黑名单  
  
**指令:**  

```
添加/删除屏蔽词 词1 词2 词3 ...

查看临时黑名单

解除屏蔽 qq1 qq2 qq3 ...
```

P.S. `解除屏蔽` 可以解除临时屏蔽, 也可以解除禁言(当然, 需要bot为群管理).  
  
你说从聊天界面查看屏蔽词库? 噢, 我亲爱的老伙计, 你怕是疯了!  


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


### DirectLinker  群文件直链提取
抄自 [ninthseason](https://github.com/ninthseason) 的 [DirectLinker](https://github.com/ninthseason/nonebot-plugin-directlinker)  
**使用方法:** [▶传送门](https://github.com/ninthseason/nonebot-plugin-directlinker#%E7%94%A8%E6%B3%95)  


### echo  说
**使用方法:**  
`@机器人` 并加上 **冒号** `：` 发送你想让机器人说的话
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


### groupmanage 群管理
  

<details>
  <summary>使用方法(点击展开)</summary>

.  
- 禁言 @qq @qq1 @qq2 X分钟(/小时/天)
- 解除禁言 @qq @qq1 @qq2
- 我要自闭 X分钟
- 开启全员禁言
- 解除全员禁言
- 升为管理 @qq @qq1 @qq2
- 取消管理 @qq @qq1 @qq2
- 修改名片 @qq @qq1 @qq2 XXX
- 修改头衔 @qq @qq1 @qq2 XXX
- 申请头衔 XXX
- 移出群聊 @qq @qq1 @qq2
- @bot 退群 qq qq1 qq2


</details>


### blacklist  黑名单
  

<details>
  <summary>使用方法(点击展开)</summary>

.  

拉黑:  
```
拉黑用户 qq qq1 qq2
拉黑群 qq qq1 qq2
拉黑所有群
拉黑所有好友
```
  
解禁:  
```
解禁用户 qq qq1 qq2
解禁群 qq qq1 qq2
解禁所有群
解禁所有好友
```
  
查看黑名单:  
```
查看用户黑名单
查看群聊黑名单

重置黑名单
```
群内发送 **`/静默`**, **`/响应`** 可快捷拉黑/解禁当前群聊  
`拉黑/解禁所有` 只对Bot添加的群/好友生效  

</details>


### rss  订阅
抄自 [Quan666](https://github.com/Quan666) 的 [ELF_RSS](https://github.com/Quan666/ELF_RSS)  
**使用方法:** [▶传送门](https://github.com/Quan666/ELF_RSS/blob/2.0/docs/2.0%20%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md)  


### simplemusic  点歌
抄自 [wq佬](https://github.com/MeetWq) 的 [SimpleMusic](https://github.com/noneplugin/nonebot-plugin-simplemusic)  
**使用方法:**  
```
点歌/qq点歌/网易点歌/酷我点歌/酷狗点歌/咪咕点歌/b站点歌 + 关键词
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
1. 安装系统
2. 安装3.9版本以上的Python
3. 下载本项目到本地
- **需要注意的是: 请确保将本项目放在纯英文的路径下.**  
如果你不知道什么叫做**路径**, 建议你把电脑放进水里泡一下.
4. 打开本项目所在目录
5. 打开**隐藏文件** `.env.dev`, 填写以下信息:  

<details>
  <summary>点击展开</summary>

.  

```
SUPERUSERS=[""]
```
在引号里填写用于控制bot的超级用户QQ  
可填写多个 例如: ["123456","654321"]  

```
ANTI_FLASH_GROUP=[""]
```
引号里填写默认开启 反闪照 的群聊, 可留空.  
可填写多个 例如: ["123456","654321"]  

```
SAUCENAO_API_KEY=""
```
在引号里填写你在 `saucenao.com` 申请到的 `apikey` , 必填, 否则无法正常使用搜图.  

```
EXHENTAI_COOKIES=""
```
在引号里填写你的 `exhentai` `cookies` , 可留空.  

```
CAIYUNAI_APIKEY=""
```
在引号里填写你的 彩云小梦 `apikey` , 必填, 否则无法正常使用小梦续写功能.  
  
  
.  

</details>
  
6. 在命令行 `cd` 到本项目的目录
7. 输入 `pip install -r requirements.txt` 安装环境依赖
8. 输入 `python bot.py` 启动机器人
9. 另开一个命令行窗口, `cd` 到本项目下的 `gocq` 文件夹
10. 运行适用于你的系统的 `go-cqhttp` 文件
- 你也可以在 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases) 下载最新的`go-cqhttp` 文件, 并放入该文件夹.
11. 用 `手机QQ` 扫码登入
12. 登入成功后, 用你的 `超级用户` 账号 给bot发 `/ping`  
如果bot给你回复 `I'm fine`, 那么就大功告成了.


### ⚠注意
**如果你是第一次使用go-cqhttp, 可能会遇到以下情况:**

- 登录失败，提示 `请在常用的设备上登录`
- 密码没有输错, 帐号未被冻结, 但是提示 `密码错误或账号被冻结`

**你可能需要进行以下步骤:**

1. 将电脑和手机处在同一IP环境下
 - 比如手机和电脑使用同一个WiFi, 或者电脑连接手机的热点.
2. 选择扫码登入
  
**服务器用户同理:**

3. 下载win版的go-cqhttp到自己电脑上
4. 按照上面的步骤1,2操作
5. 登入成功后把生成的文件拷到服务器上


### ⚠喜报
你可能会遇到以下问题:

- 私聊机器人收得到消息，但是群聊收不到

此时请查看go-cqhttp的运行窗口, 你可能会看到这样一条消息:
```
[WARNING]: 群消息发送失败: 账号可能被风控.
```

解决办法:

- 挂几天试试  
万一企鹅大发慈悲给你解除风控了呢

- 企业账号  
企业账号是不会风控的，就是开通费有亿点点贵。

- 换个号  
换个qq号吧，就当续命了
