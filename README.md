
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
- [x] **嘴臭屏蔽** - anti abuse

  <details>
    <summary>指令表</summary>

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
    <summary>指令表</summary>

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

  群内发送 **`/静默`**, **`/响应`** 可快捷拉黑/解禁当前群聊

  `拉黑/解禁所有` 只对已添加的群/好友生效

  </details>

- [x] **好友/群聊管理** - manager

  <details>
    <summary>指令表</summary>

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
  撤回   (回复消息发送`撤回`)
  ```

  **以下命令需要前缀 `/`**
  ```
  同意(拒绝)好友 QQ号 备注
  同意(拒绝)拉群 FLAG
  [群聊] 同意(拒绝)入群 FLAG 理由
  (`备注` 和 `理由` 可省略)

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
  退群 qq qq1 qq2 ... (群号不存在时则退出当前群聊)
  删除好友 qq qq1 qq2 ...
  删除单向好友 qq qq1 qq2 ...
  查看群员列表
  设置群头像 [图片]   ⚠该API不稳定!
  ```

  </details>

- [x] **自检** - status

  <details>
    <summary>使用方法</summary>

  移植自 [摸](https://github.com/Kyomotoi) 的 [ATRI](https://github.com/Kyomotoi/ATRI), 改成了限超级用户使用

  发送 `/ping` 测试bot应答

  发送 `/status` 查看bot设备状态

  </details>

- [x] **搜图** - PicSearch

  <details>
    <summary>使用方法</summary>

  抄自 [NekoAria](https://github.com/NekoAria) 的 [YetAnotherPicSearch](https://github.com/NekoAria/YetAnotherPicSearch)

  将原插件的 **搜图** 改为 **搜图#** ，增加了隐蔽性，防止误触（x

  此外请参考原插件 [▶使用方法️️](https://github.com/NekoAria/YetAnotherPicSearch/blob/main/docs/%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md)

  </details>



## 部署方式
1. 安装系统
2. 安装3.9版本以上的Python
3. 下载本项目到本地
   - **需要注意的是: 请确保将本项目放在纯英文的路径下.**
   - 如果你不知道什么叫做**路径**, 建议你把电脑放进水里泡一下.
4. 打开本项目所在目录
5. 打开**隐藏文件** `.env`, 填写以下信息:

   <details>
     <summary>点击展开</summary>

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

   </details>

6. 在命令行 `cd` 到本项目的目录
7. 输入 `pip install -r requirements.txt` 安装环境依赖
8. 输入 `python bot.py` 启动机器人
9. 另开一个命令行窗口, `cd` 到本项目下的 `go-cqhttp` 文件夹
10. 运行适用于你的系统的 `go-cqhttp` 文件
    - 你也可以在 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases) 下载最新的 `go-cqhttp` 文件, 并放入该文件夹.
11. 用 `手机QQ` 扫码登入
12. 登入成功后, 用你的 `超级用户` 账号 给bot发 `/ping`
如果bot给你回复 `I'm fine`, 那么就大功告成了.


### ⚠注意
**如果你是第一次使用 go-cqhttp, 可能会遇到以下情况:**

- 登录失败，提示 `请在常用的设备上登录`
- 密码没有输错, 帐号未被冻结, 但是提示 `密码错误或账号被冻结`

**你可能需要进行以下步骤:**

1. 将电脑和手机处在同一IP环境下
   - 比如手机和电脑使用同一个WiFi, 或者电脑连接手机的热点.
2. 选择扫码登入

**服务器用户同理:**

3. 下载对应你电脑系统的 **go-cqhttp** 到电脑上
4. 按照上面的 **步骤1,2** 操作
5. 登入成功后把生成的 **device.json** 和 **session.token** 拷到服务器上该项目的 **go-cqhttp的文件夹里**


### ⚠喜报
你可能会遇到以下问题:

- 私聊机器人收得到消息，但是群聊收不到

此时请查看 **go-cqhttp** 的运行窗口, 你可能会看到类似这样的一条消息:
```
[WARNING]: 群消息发送失败: 账号可能被风控.
```

解决办法:

- 多挂几天, 等风控解除
- 企业帐号 (企业帐号不会风控)
- 换个帐号
