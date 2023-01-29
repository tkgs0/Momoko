# 项目构建中, 敬请期待...

# 桃桃Bot  
此项目是基于 [NoneBot2](https://github.com/nonebot/nonebot2) 和 [Walle-Q](https://github.com/onebot-walle/walle-q) 的QQ群聊娱乐机器人  
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
    <img src="https://img.shields.io/badge/OneBot-v12-black.svg" alt="OneBot">
</a>
<a href="https://github.com/onebot-walle/walle-q">
    <img src="https://img.shields.io/badge/WalleQ-0.2.5-blueviolet.svg" alt="Walle-Q">
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
- [x] **anti_abuse - 嘴臭屏蔽** (被动插件)

  <details>
    <summary>使用方法</summary>

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

  </details>

- [x] **blacklist - 黑名单**

  <details>
    <summary>使用方法</summary>

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

- [ ] **groupmanage - 群管理**

  <details>
    <summary>使用方法</summary>

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

- [ ] **status - 查看设备状态**

  <details>
    <summary>使用方法</summary>

  发送 `/ping` 测试bot应答  
  发送 `/status` 查看bot设备状态  
  超级用户使用

  </details>

- [ ] **tarot - 抽塔罗牌**

  <details>
    <summary>使用方法</summary>

  ```
  @机器人 抽塔罗牌
  ```

  </details>

- [ ] **withdraw - 撤回**

  <details>
    <summary>使用方法</summary>

  回复机器人的消息发送 `撤回`

  </details>

## 部署方式
1. 安装系统
2. 安装3.9版本以上的Python
3. 下载本项目到本地
- **需要注意的是: 请确保将本项目放在纯英文的路径下.**  
  如果你不知道什么叫做**路径**, 建议你把电脑放进水里泡一下.
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
9. 另开一个命令行窗口, `cd` 到本项目下的 `walle-q` 文件夹
10. 运行适用于你的系统的 `walle-q` 文件
    - 你也可以在 [Walle-Q](https://github.com/onebot-walle/walle-q/releases) 下载最新的`walle-q` 文件, 并放入该文件夹.
11. 用 `手机QQ` 扫码登入
12. 登入成功后, 用你的 `超级用户` 账号 给bot发 `/ping`  
如果bot给你回复 `I'm fine`, 那么就大功告成了.


### ⚠注意
**如果你是第一次使用walle-q, 可能会遇到以下情况:**

- 登录失败，提示 `请在常用的设备上登录`
- 密码没有输错, 帐号未被冻结, 但是提示 `密码错误或账号被冻结`

**你可能需要进行以下步骤:**

1. 将电脑和手机处在同一IP环境下
   - 比如手机和电脑使用同一个WiFi, 或者电脑连接手机的热点.
2. 选择扫码登入
  
**服务器用户同理:**

3. 下载对应你电脑系统的walle-q到电脑上
4. 按照上面的 **步骤1,2** 操作
5. 登入成功后把生成的data文件夹拷到服务器上该项目的 **walle-q的文件夹里**


### ⚠喜报
你可能会遇到以下问题:

- 私聊机器人收得到消息，但是群聊收不到

此时请查看walle-q的运行窗口, 你可能会看到类似这样的一条消息:
```
群消息发送失败: 账号可能被风控.
```

解决办法:

- 挂几天试试  
万一企鹅大发慈悲给你解除风控了呢

- 企业账号  
企业账号是不会风控的，就是开通费有亿点点贵。

- 换个号  
换个qq号吧，就当续命了
