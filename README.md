
# 桃桃Bot
此项目是基于 [NoneBot2](https://github.com/nonebot/nonebot2) 和 [OneBot.v11](https://onebot.adapters.nonebot.dev) 的QQ群聊娱乐机器人  
借(chao)鉴(xi)了大佬们的代码，实现了一些对群友的娱乐功能和实用功能（大概

<div>

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/tkgs0/Momoko.svg" alt="License">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
</a>
<a href="https://nonebot.dev">
    <img src="https://img.shields.io/badge/NoneBot-2.2.1+-red.svg" alt="NoneBot">
</a>
<a href="https://onebot.adapters.nonebot.dev">
    <img src="https://img.shields.io/badge/OneBot-v11-black.svg" alt="OneBot">
</a>

</div>


# NoneBot2

<div>
<a href="https://nonebot.dev">
    <img style="height: 150px;width: 150px;" src="https://nonebot.dev/logo.png" alt="NoneBot">
</a>

非常 [ **[NICE](https://github.com/nonebot/nonebot2)** ] 的Bot框架

</div>


## 声明
此项目仅用于学习交流，不可商用以及非法用途


## 功能表
本项目支持使用 `nb-cli` 从 [nonebot插件商店](https://nonebot.dev/store) 安装插件

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

- [x] **黑名单** - blacklist

  <details>
    <summary>使用方法</summary>

  基于 [A-kirami](https://github.com/A-kirami) 的 [黑白名单](https://github.com/A-kirami/nonebot-plugin-namelist) 魔改(?)的仅黑名单插件

  超级用户不受黑名单影响

  拉黑:
  ```
  拉黑用户 qq qq1 qq2
  拉黑群 qq qq1 qq2
  拉黑私聊 qq qq1 qq2
  拉黑所有群
  拉黑所有好友

  私聊静默/私聊禁用/静默私聊/禁用私聊
  ```

  解禁:
  ```
  解禁用户 qq qq1 qq2
  解禁群 qq qq1 qq2
  解禁私聊 qq qq1 qq2
  解禁所有群
  解禁所有好友

  私聊响应/私聊启用/响应私聊/启用私聊
  ```

  查看黑名单:
  ```
  查看用户黑名单
  查看群聊黑名单
  查看私聊黑名单

  重置黑名单        # 重置当前Bot帐号对应的黑名单
  重置所有黑名单    # 清空黑名单数据库
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

  [群聊] 同意(拒绝)入群 FLAG 理由    # `理由` 可省略
  [群聊] 入群自动同意(拒绝)
  [群聊] 关闭入群自动

  [群聊] 入群欢迎开(关)
  [群聊] 退群播报开(关)
  [群聊] 设置欢迎词 xxxxx
  [群聊] 查看欢迎词
  ```

  **以下命令需要 `@机器人`** (私聊不用)
  ```
  同意(拒绝)好友 FLAG 备注    # `备注` 可省略
  同意(拒绝)拉群 FLAG

  查看好友(群聊)请求
  清空好友(入群/拉群)请求

  好友(拉群)自动同意(拒绝)
  关闭好友(拉群)自动

  重置请求自动

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

  </details>

- [x] **关键词禁言** - keyword ban

  <details>
    <summary>使用方法</summary>

  ```
    /启用(禁用)keyban
    # 关键词禁言服务开关
  ```
  可批量添加多个关键词, 以换行隔开
  ```
    关键词(/正则)禁言 XX分(/时/日/月)
    ocr
    内容1
    内容2
    内容3
  ```
  ```
    删除禁言关键词(/正则)
    内容1
    内容2
    内容3
  ```
  ```
    查看禁言关键词(/正则)
  ```
  ```
    清理群禁言规则 qq qq1 qq2 ...
    # 用于清理已炸或已退出的群聊残留的规则
  ```
  ```
    /reset_keyword_ban_db
    # 重置数据库
  ```

  示例:
  ```
    关键词禁言 1天
    吃柠檬
    尼玛
    群主是沙壁
    来点🐍图
  ```
  ```
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
  /sh {命令}
  ```
  ```
  /cmd {命令}
  ```

  示例:

  ```
  /sh echo "Hello World"
  ```
  ```
  /cmd echo "Hello World"
  ```

  </details>

- [x] **说** - echo

  <details>
    <summary>使用方法</summary>

  `@机器人` 并加上 **冒号** `：` 发送你想让机器人说的话

  ```
  @桃桃酱 ：xxxxx
  ```

  为防止用户滥用导致封号，限制仅超级用户可用

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

- [x] **闲聊** - smart reply

  <details>
    <summary>使用方法</summary>

  抄自 [Special-Week](https://github.com/Special-Week) 的 [SmartReply](https://github.com/Special-Week/nonebot_plugin_smart_reply)

  `@机器人` + 你想对机器人说的骚话

  ```
  @桃桃酱 不可以色色

  设置回复模式 小思/小爱
  ```

  </details>

- [x] **塔罗牌** - tarot

  <details>
    <summary>使用方法</summary>

  ```
  @机器人 抽塔罗牌
  ```

  </details>


- [x] **B链解析** - bv2mp4

  <details>
    <summary>使用方法</summary>

  基于 [汣度](https://github.com/j1udu) 的 [bili2mp4](https://github.com/j1udu/nonebot-plugin-bili2mp4) 魔改的 bv2mp4
  <br><br>
  将群友分享的B站链接解析为视频文件并发送

  ```
  b2v:
      -s  插件开关
      -c  设置cookies  # 至少需要包含 SESSDATA, bili_jct, DedeUserID, buvid3/buvid4
      -p  设置清晰度  # 360/480/720/1080, 0 为不限制
      -x  设置文件限制  # 默认 72 (MB), 0 为不限制
      -l  查看列表
      -r  重置列表
  ```

  </details>


## 部署方式
1. 安装系统

   | 推荐 | 不推荐 |
   |:-----:|:----:|
   | Debian 11 以上 | Debian 10 以下 |
   | Ubuntu 20 以上 | Ubuntu 18 以下 |
   | Windows 10 以上 | CentOS |
   | MacOS | |

2. 安装3.10版本以上的Python, 安装 **ffmpeg**, 以及 **libEGL**  
   并正确配置环境变量

3. 下载本项目到本地
   - **需要注意的是: 请确保将本项目放在纯英文、数字、下划线的路径下.**
   - 如果你不知道什么叫做**路径**, 建议你把电脑放进水里泡一下.

4. 打开本项目所在目录

5. 打开**隐藏文件** `.env`, 按注释填写相关项

6. 在命令行 `cd` 到本项目的目录

7. 创建一个Python3.10以上的虚拟环境, 并安装依赖

   <details>
     <summary>使用pip安装</summary>

   ```bash
   pip install -U -r requirements.txt
   ```

   </details>

   <details>
     <summary>使用环境管理器安装</summary>

   ```bash
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
     <summary>环境管理器启动</summary>

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

9. 另开一个命令行窗口, 配置 **兼容 OneBot.v11 的协议端**. 
   至于什么是 *协议端* ? 由于某些不可抗力, 我不能给大伙细说, 请自行探索.

10. 在你的协议端配置 `反向ws` **监听地址** 以及 **Token**, 
    需要与机器人目录下的 `.env` 配置一致.

11. 保存并关闭文件

12. 运行**协议端**, 登入成功后, 如果bot主动私聊超级用户说 `早ﾉ🌞`, 那么就大功告成了.
