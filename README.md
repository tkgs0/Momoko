
# 桃桃Bot
此项目是基于 [NoneBot2](https://github.com/nonebot/nonebot2) 和 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的QQ群聊娱乐机器人  
借(chao)鉴(xi)了大佬们的代码，实现了一些对群友的娱乐功能和实用功能（大概

<div>

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/tkgs0/Momoko.svg" alt="License">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
</a>
<a href="https://https://v2.nonebot.dev">
    <img src="https://img.shields.io/badge/NoneBot-2.0.0-red.svg" alt="NoneBot">
</a>
<a href="https://onebot.adapters.nonebot.dev">
    <img src="https://img.shields.io/badge/OneBot-v11-black.svg" alt="OneBot">
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


## 功能表
本项目支持使用 `nb-cli` 从 [nonebot插件商店](https://v2.nonebot.dev/store) 安装插件

- [ ] **插件控制**  
  ~~暂时没有~~

- [x] **涩图** - setu

  <details>
    <summary>使用方法</summary>

  ```
  /setu {数量} {关键词}

  私聊(群聊)启用(禁用)涩图 qq qq1 qq2 ...
  查看涩图设置
  切换涩图api       # lolicon, acggov
  启用(禁用)涩图    # 在当前会话启用(禁用)涩图
  重置涩图          # 重置涩图设置
  ```

  示例:

  ```
  /setu                         # 来1张涩图
  /setu 3                       # 来3张涩图
  /setu 阿波尼亚                # 来1张 '阿波尼亚' 的涩图
  /setu 3 阿波尼亚              # 来3张 '阿波尼亚' 的涩图
  /setu 3 R-18 阿波尼亚 水着    # 来3张 '水着','阿波尼亚','R-18' 的涩图
  ```

  </details>

- [x] **嘴臭屏蔽** - anti abuse

  <details>
    <summary>使用方法</summary>

  检测到有用户 `@机器人` 并嘴臭时将其临时屏蔽(bot重启后失效)

  当bot为群管理时会请对方喝昏睡红茶(禁言)

  - 超级用户不受临时屏蔽影响 _~~但是会被昏睡红茶影响~~_
  - 当bot的群权限比超级用户高的时候, 超级用户也有机会品尝昏睡红茶
  - 被bot灌了昏睡红茶的用户不会进临时黑名单
  - 开启 **`对线模式`** 后不会被bot灌昏睡红茶和临时拉黑 (~~因为要对线~~)

  <table> 
    <tr align="center">
      <th> 指令 </th>
      <th> 权限 </th>
      <th> 需要@ </th>
      <th> 范围 </th>
      <th> 说明 </th>
    </tr>
    <tr align="center">
      <td> ^(添加|删除)屏蔽词 xxx </td>
      <td> 主人 </td>
      <td> 否 </td>
      <td> 私聊 | 群聊 </td>
      <td rowspan="2"> 可输入多个,<br>用空格隔开 </td>
    </tr>
    <tr align="center">
      <td> 解除屏蔽 qq </td>
      <td> 主人 </td>
      <td> 否 </td>
      <td> 私聊 | 群聊 </td>
    </tr>
    <tr align="center">
      <td> 查看临时黑名单 </td>
      <td> 主人 </td>
      <td> 否 </td>
      <td> 私聊 | 群聊 </td>
      <td> </td>
    </tr>
    <tr align="center">
      <td> ^(禁用|启用)飞(妈|马|🐴|🐎)令 </td>
      <td> 主人 </td>
      <td> 否 </td>
      <td> 私聊 | 群聊 </td>
      <td> 开启/关闭对线模式 </td>
  </table>

  P.S. `解除屏蔽` 可以解除临时屏蔽, 也可以解除禁言(当然, 需要bot为群管理).

  你说从聊天界面查看屏蔽词库? 噢, 我亲爱的老伙计, 你怕是疯了!

  </details>

- [x] **黑名单** - blacklist

  <details>
    <summary>使用方法</summary>

  基于 [A-kirami](https://github.com/A-kirami) 的 [黑白名单](https://github.com/A-kirami/nonebot-plugin-namelist) 魔改(?)的仅黑名单插件

  超级用户不受黑名单影响

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

  被禁言自动屏蔽该群:
  ```
  自觉静默开
  自觉静默关
  ```

  群内发送 **`/静默`**, **`/响应`** 可快捷拉黑/解禁当前群聊

  `拉黑/解禁所有` 只对已添加的群/好友生效

  </details>

- [x] **好友/群聊管理** - manager

  <details>
    <summary>使用方法</summary>

  ```
  踢出群聊 @qq @qq1 @qq2 ...
  禁言 @qq @qq1 @qq2 ... XX分钟(/小时/天)
  解除禁言 @qq @qq1 @qq2 ...
  我要自闭 XX分钟(/小时/天)
  开启(关闭)全员禁言
  设为(撤销)管理 @qq @qq1 @qq2 ...
  允许(禁止)匿名
  修改名片(头衔) @qq @qq1 @qq2 ... XXXX
  设置群名 XXXX
  申请头衔 XXXX
  撤回    # 回复消息发送`撤回`
  ```

  **以下命令需要前缀 `/`**
  ```
  同意(拒绝)好友 FLAG 备注
  同意(拒绝)拉群 FLAG
  [群聊] 同意(拒绝)入群 FLAG 理由
  ## `备注` 和 `理由` 可省略

  查看好友(群聊)请求
  清空好友(入群/拉群)请求

  好友(拉群)自动同意(拒绝)
  关闭好友(拉群)自动

  [群聊] 入群自动同意(拒绝)
  [群聊] 关闭入群自动

  重置请求自动
  ```

  **以下命令需要 `@机器人`** (私聊不用)
  ```
  设置网名 XXXX
  查找好友(群) qq qq1 qq2 ...
  查看所有好友(群)
  查看单向好友
  退群 qq qq1 qq2 ...    # 未输入群号则退出当前群聊
  删除好友 qq qq1 qq2 ...
  删除单向好友 qq qq1 qq2 ...
  查看群员列表
  设置群头像[图片]    # ⚠该API不稳定!
  ```


  **关键词禁言**  
  可批量添加多个关键词, 以换行隔开
  ```
  使用方式:
    关键词(/正则)禁言 XX分(/时/日/月)
    [ocr]
    内容1
    内容2
    内容3
  
    删除禁言关键词(/正则)
    内容1
    内容2
    内容3
  
    查看禁言关键词(/正则)
  
    清理群禁言规则 qq qq1 qq2 ...
    # 用于清理已炸或已退出的群聊残留的规则
  
    /reset_keyword_ban_db
    # 重置数据库
  
  示例:
    关键词禁言 1天
    吃柠檬
    尼玛
    群主是沙壁
    来点🐍图
  
    正则禁言 30天
    http(s)?://.*
    .*(是|做).+的(狗|猫)
  ```

  </details>

- [x] **自检** - status

  <details>
    <summary>使用方法</summary>

  移植自 [摸](https://github.com/Kyomotoi) 的 [ATRI](https://github.com/Kyomotoi/ATRI), 改成了限超级用户使用

  ```
  /ping    # 测试bot应答

  /status    # 查看bot设备状态
  ```

  </details>

- [x] **调用命令行** - sys cmd

  <details>
    <summary>使用方法</summary>

  调用系统命令行

  ⚠危险操作, 谨慎使用!

  ```
  >shell {命令}
  ```

  示例:

  ```
  >shell echo "Hello World"
  ```

  </details>

- [x] **说** - echo

  <details>
    <summary>使用方法</summary>

  `@机器人` 并加上 **冒号** `：` 发送你想让机器人说的话

  ```
  @桃桃酱 ：xxxxx
  ```

  为防止恶意用户滥用导致封号，限制仅超级用户可用

  </details>

- [x] **B链解析** - analysis bilibili

  <details>
    <summary>使用方法</summary>

  ［被动插件］

  抄自 [mengshouer](https://github.com/mengshouer)/[analysis\_bilibili](https://github.com/mengshouer/nonebot_plugin_analysis_bilibili) 的 [NekoAria修改版](https://github.com/NekoAria/nonebot_plugin_analysis_bilibili)

  自动解析聊天中发送的 bilibili 小程序/链接

  [▶使用方法](https://github.com/NekoAria/nonebot_plugin_analysis_bilibili#%E4%BD%BF%E7%94%A8%E6%96%B9%E5%BC%8F)

  </details>

- [x] **反闪照** - anti flash

  <details>
    <summary>使用方法</summary>

  抄自 [KafCoppelia](https://github.com/MinatoAquaCrews) 的 [AntiFlash](https://github.com/MinatoAquaCrews/nonebot_plugin_antiflash)

  在`env`内设置：

  ```python
  ANTI_FLASH_ON=true                          # 全局开关
  ANTI_FLASH_GROUP=["123456789", "987654321"] # 默认开启的群聊，但可通过指令开关
  ANTI_FLASH_PATH="your-path-to-config.json"  # 配置文件路径，默认同插件代码路径
  ```

  `ANTI_FLASH_GROUP` 会在每次初始化时写入配置文件，在群组启用反闪照，可通过指令更改。

  **修改** 配置文件即读即改，可后台修改。

  - 全局开关**仅超管**配置，不支持指令修改全局开关；
  - 各群聊均配置开关，需**管理员及超管权限**进行修改；

  指令:

  ```
  开启/启用/禁用反闪照
  ```

  </details>

- [x] **反撤回** - anti recall

  <details>
    <summary>使用方法</summary>

  移植自 [摸](https://github.com/Kyomotoi) 的 [ATRI](https://github.com/Kyomotoi/ATRI)

  将检测到的撤回消息转发给超级用户

  </details>

- [x] **彩云小梦** - caiyun ai

  <details>
    <summary>使用方法</summary>

  抄自 [wq佬](https://github.com/MeetWq) 的 [caiyunai](https://github.com/noneplugin/nonebot-plugin-caiyunai)

  **配置:**

  需要在 `.env` 文件中添加彩云小梦apikey：

  ```
  CAIYUNAI_APIKEY=xxx
  ```

  apikey获取：

  前往 http://if.caiyunai.com/dream 注册彩云小梦用户；

  注册完成后，F12打开开发者工具；

  在控制台中输入 `alert(localStorage.cy_dream_user)` ，弹出窗口中的 uid 即为 apikey；

  或者进行一次续写，在 Network 中查看 novel\_ai 请求，Payload 中的 uid 项即为 apikey。


  **使用:**
  ```
  @机器人 续写/彩云小梦 xxx
  ```

  </details>

- [x] **在线跑代码** - code runner

  <details>
    <summary>使用方法</summary>

  移植自 [摸](https://github.com/Kyomotoi) 的 [ATRI](https://github.com/Kyomotoi/ATRI)

  ```
  >code {语言}
  {代码}
  ```

  示例:

  ```
  >code python
  print('hello world')
  ```

  发送 `>code.list` 查看支持的语言

  </details>

- [x] **群文件直链提取** - direct linker

  <details>
    <summary>使用方法</summary>

  抄自 [ninthseason](https://github.com/ninthseason) 的 [DirectLinker](https://github.com/Utmost-Happiness-Planet/nonebot-plugin-directlinker)

  [▶使用方法](https://github.com/Utmost-Happiness-Planet/nonebot-plugin-directlinker#%E7%94%A8%E6%B3%95)

  </details>

- [x] **合并转发** - fake msg

  <details>
    <summary>使用方法</summary>

  移植自 [摸](https://github.com/Kyomotoi) 的 [ATRI](https://github.com/Kyomotoi/ATRI)

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

  </details>

- [x] **你看我像** - look like

  <details>
    <summary>使用方法</summary>

  `@机器人` 发送 `你看我像`

  ```
  @桃桃酱 你看我像人吗？
  ```

  </details>

- [x] **搜图** - PicSearch

  <details>
    <summary>使用方法</summary>

  抄自 [NekoAria](https://github.com/NekoAria) 的 [YetAnotherPicSearch](https://github.com/NekoAria/YetAnotherPicSearch)

  请参考原插件 [▶使用方法️️](https://github.com/NekoAria/YetAnotherPicSearch/blob/main/docs/%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md)

  </details>

- [x] **RSS订阅** - rss

  <details>
    <summary>使用方法</summary>

  抄自 [Quan666](https://github.com/Quan666) 的 [ELF\_RSS](https://github.com/Quan666/ELF_RSS)

  [▶使用方法](https://github.com/Quan666/ELF_RSS/blob/2.0/docs/2.0%20%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md)

  </details>

- [x] **点歌** - simplemusic

  <details>
    <summary>使用方法</summary>

  抄自 [wq佬](https://github.com/MeetWq) 的 [SimpleMusic](https://github.com/noneplugin/nonebot-plugin-simplemusic)

  ```
  点歌/qq点歌/网易点歌/酷我点歌/酷狗点歌/咪咕点歌/b站点歌 + 关键词
  ```

  示例:

  ```
  点歌 朝你大胯捏一把
  ```

  默认为qq点歌

  </details>

- [x] **闲聊** - smart reply

  <details>
    <summary>使用方法</summary>

  抄自 [Special-Week](https://github.com/Special-Week) 的 [SmartReply](https://github.com/Special-Week/nonebot_plugin_smart_reply)

  `@机器人` + 你想对机器人说的骚话

  ```
  @桃桃酱 不可以色色
  ```

  </details>

- [x] **塔罗牌** - tarot

  <details>
    <summary>使用方法</summary>

  ```
  @机器人 抽塔罗牌
  ```

  </details>

- [x] **词库问答** (你问我答) - wordbank

  <details>
    <summary>使用方法</summary>

  抄自 [kexue](https://github.com/kexue-z) 的 [wordbank2](https://github.com/kexue-z/nonebot-plugin-word-bank2)

  [▶使用方法](https://github.com/kexue-z/nonebot-plugin-word-bank2#%E5%BC%80%E5%A7%8B%E4%BD%BF%E7%94%A8)

  </details>


## 部署方式
1. 安装系统

   | 推荐 | 不推荐 |
   |:-----:|:----:|
   | Debian 11 以上 | Debian 10 以下 |
   | Ubuntu 20 以上 | Ubuntu 18 以下 |
   | Windows 10 以上 | CentOS |
   | MacOS | |

2. 安装3.9版本以上的Python, 安装ffmpeg(bot发语音需要), 并正确配置环境变量

3. 下载本项目到本地
   - **需要注意的是: 请确保将本项目放在纯英文、数字、下划线的路径下.**
   - 如果你不知道什么叫做**路径**, 建议你把电脑放进水里泡一下.

4. 打开本项目所在目录

5. 打开**隐藏文件** `.env`, 填写以下信息:

   <details>
     <summary>点击展开</summary>

   ```env
   SUPERUSERS=[""]  # 填写用于控制bot的超级用户QQ
   # 可填写多个 例如: ["123456","654321"]

   NICKNAME=["桃桃", "桃桃酱"]  # 机器人的昵称

   SETU_COOLDOWN=60  # 涩图的响应cd 为0则无冷却
   SETU_WITHDRAW=60  # 涩图的撤回cd < 120 为0则不撤回

   LOLICON_R18=2  # Lolicon API设置
   # 0为非R18，1为R18，2为混合（在库中的分类，不等同于作品本身的 R-18 标识）

   PIXPROXY=""  # pximg图片代理, 需要填写前缀 https:// 或 http://
   # 留空为直连 i.pximg.net

   ACGGOV_TOKEN="apikey"

   ANTI_FLASH_GROUP=[]  # 填写默认开启 反闪照 的群聊, 可留空.
   # 可填写多个 例如: ["123456","654321"]

   SAUCENAO_API_KEY=""  # 在引号里填写你在 saucenao.com 申请到的 apikey
   # 缺少该项将无法正常使用搜图.

   EXHENTAI_COOKIES=""  # 在引号里填写你的 exhentai cookies, 可留空.

   CAIYUNAI_APIKEY=""  # 在引号里填写你的 彩云小梦 apikey
   # 缺少该项将无法正常使用小梦续写功能.

   LINKER_GROUP=[]  # 填写启用群文件直链插件的群
   LINKER_COMMAND="link"  # 设置插件触发命令（默认`link`）
   ```

   </details>

6. 在命令行 `cd` 到本项目的目录

7. 安装环境依赖 · 二选一

   <details>
     <summary>使用pip安装</summary>

   ```bash
   pip install -r requirements.txt
   ```

   </details>
   <details>
     <summary>使用poetry安装 (推荐)</summary>

   ```bash
   pip install --upgrade poetry
   poetry install
   ```

   </details>

8. 启动机器人  
   **根据你的安装方式选择启动方式**

   <details>
     <summary>常规启动</summary>

     ```bash
     python bot.py
     ```
     **或者**
     ```bash
     nb run
     ```

   </details>
   <details>
     <summary>poetry启动</summary>

     ```bash
     poetry run python bot.py
     ```
     **或者**
     ```bash
     poetry run nb run
     ```
     **或者**
     ```bash
     poetry shell
     python bot.py
     ```
     **或者**
     ```bash
     poetry shell
     nb run
     ```

   </details>

9. 另开一个命令行窗口, `cd` 到本项目下的 `go-cqhttp` 文件夹

10. 运行适用于你的系统的 `go-cqhttp` 文件
    - 你也可以在 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases) 下载最新的 `go-cqhttp` 文件, 并放入该文件夹.

11. 在 gocq 的 **config.yml** 填写Bot的**帐号**和**密码**, 保存并关闭文件

12. 运行**go-cqhttp**, 登入成功后, 用你的 `超级用户` 账号 给bot发 `/ping`

如果bot给你回复 `I'm fine`, 那么就大功告成了.


### ⚠注意
**你可能会遇到以下情况:**

- 登录失败，提示 `请在常用的设备上登录`
- 密码没有输错, 帐号未被冻结, 但是提示 `密码错误或账号被冻结`
- 提示 `当前使用的QQ版本过低` 等等一些奇奇怪怪的问题导致的登入失败

**你可能需要进行以下步骤:**

1. 进入 **go-cqhttp** 所在的文件夹

2. 将电脑和手机处在同一IP环境下
   - 比如手机和电脑使用同一个WiFi, 或者电脑连接手机的热点.

3. 删除可能存在的 `device.json` `session.token` `data` 文件/文件夹

- 如果你使用的是 `1.0.0-rc4` 以及更低版本的 `go-cqhttp` 生成的 `config.yml`,  
  请将其删除并重新运行 `go-cqhttp` 生成新的 `config.yml`,  
  然后正确配置 `config.yml` 并重复步骤**3**

4. 运行文件夹里的 [HomoOS.py](https://github.com/tkgs0/Momoko/blob/main/gocq/HomoOS.py) 生成新的 **device.json**
   - 协议类型请参考 go-cqhttp 的[设备信息](https://docs.go-cqhttp.org/guide/config.html#设备信息)

   <details>
     <summary>点击展开</summary>
     <table>
     <thead>
     <tr>
     <th>值</th>
     <th>类型</th>
     <th>限制</th>
     </tr>
     </thead>
     <tbody>
     <tr>
     <td>0</td>
     <td>Default/Unset</td>
     <td>当前版本下默认为aPad</td>
     </tr>
     <tr>
     <td>1</td>
     <td>Android Phone</td>
     <td>无</td>
     </tr>
     <tr>
     <td>2</td>
     <td>Android Watch</td>
     <td>无法接收 <code>notify</code> 事件、无法接收口令红包、无法接收撤回消息</td>
     </tr>
     <tr>
     <td>3</td>
     <td>MacOS</td>
     <td>无</td>
     </tr>
     <tr>
     <td>4</td>
     <td>企点</td>
     <td>只能登录企点账号或企点子账号</td>
     </tr>
     <tr>
     <td>5</td>
     <td>iPad</td>
     <td>无</td>
     </tr>
     <tr>
     <td>6</td>
     <td>aPad</td>
     <td>无</td>
     </tr>
     </tbody>
     </table>
   </details>

5. 在 [mirai-login-solver-sakura](https://github.com/KasukuSakura/mirai-login-solver-sakura/releases) 下载最新版本的 **apk-release.apk** 安装到手机
   - 同样需要该手机**与go-cqhttp所在设备处于同一IP环境下**

6. 重新运行 **go-cqhttp**, 在弹出以下提示时**输入2**, 并按下你键盘上的回车(Enter)
   ```
   [2023-03-18 11:45:14] [WARNING]: 登录需要滑条验证码, 请验证后重试.
   [2023-03-18 11:45:14] [WARNING]: 请选择提交滑块ticket方式:
   [2023-03-18 11:45:14] [WARNING]: 1. 自动提交
   [2023-03-18 11:45:14] [WARNING]: 2. 手动抓取提交
   [2023-03-18 11:45:14] [WARNING]: 请输入(1 - 2)：
   2
   ```
   此时控制台将输出一串链接, 将该链接**完整地复制**到上一步安装的app `Sakura Login Solver`, 并点击 **下一步**,  
  
   在经过1次或者2次滑块验证后, 将弹出的 token 复制并粘贴到控制台, 并按下你键盘上的回车(Enter)  

   <details>
     <summary>不知道如何将文本复制到手机?</summary>

   如果你笨到不知道如何将文本从电脑复制到手机, 我可以提示你一下: 你可以用电脑上登入的QQ发送文本消息给手机上登入的QQ

   </details>

7. 你可能会看到类似以下信息:
   ```
   [2023-03-21 07:50:39] [WARNING]: 账号已开启设备锁，请选择验证方式:
   [2023-03-21 07:50:39] [WARNING]: 1. 向手机 *********** 发送短信验证码
   [2023-03-21 07:50:39] [WARNING]: 2. 使用手机QQ扫码验证.
   [2023-03-21 07:50:39] [WARNING]: 请输入(1 - 2)：
   1
   ````
   输入**1**选择**短信验证**, 并按下你键盘上的回车(Enter),  
  
   此时你Bot绑定的手机将会收到一条验证码短信,  
  
   将你收到的验证码输入到控制台, 并按下你键盘上的回车(Enter)

**服务器用户同理:**

8. 下载对应你电脑系统的 **go-cqhttp** 到电脑上

9. 按照上面的 **步骤1~7** 操作

10. 登入成功后把生成的 **device.json** 和 **session.token** 拷到服务器上该项目使用的**go-cqhttp所在的文件夹里**


### ⚠喜报
你可能会遇到以下问题:

- 私聊机器人能正常回复消息，但是群聊发不出

此时请查看 **go-cqhttp** 的运行窗口, 你可能会看到类似这样的一条消息:
```
[WARNING]: 群消息发送失败: 账号可能被风控.
```

解决办法:

- 多挂几天, 等风控解除
- 企业帐号 (企业帐号不会风控)
- 换个帐号
