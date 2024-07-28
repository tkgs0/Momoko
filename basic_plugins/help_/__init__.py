import nonebot
from nonebot.rule import to_me
from nonebot.plugin import on_command, PluginMetadata
from nonebot.params import CommandArg
from nonebot.internal.adapter import Message


usage: str ="""

⛦ 🍑 Momoko 开源 Project ⛥
* OneBot + NoneBot + Python
* Copyright © 2021 - 2023 tkgs0. All Rights Reserved.
* 项目地址: https://github.com/tkgs0/Momoko

菜单指令:
·help list    # 查看服务列表
·help <服务名>    # 查看指定服务的帮助信息

""".strip()


# 本插件抄自 https://github.com/XZhouQD/nonebot-plugin-help

__plugin_meta__ = PluginMetadata(
    name="插件菜单",
    description="",
    usage=usage,
    type="application"
)


h = on_command(
    "help",
    rule=to_me(),
    aliases={"帮助", "服务", "幫助", "服務", "菜单", "菜單"},
    priority=2, block=True
)


@h.handle()
async def _(args: Message = CommandArg()):
    if not (arg := args.extract_plain_text()):
        await h.finish(usage)

    if arg.lower() in ['ls', 'list', '列表']:
        plugins = nonebot.get_loaded_plugins()
        plugin_names = []
        for plugin in plugins:
            # plugin.name, then metadata name or legacy help name
            name = f'{plugin.name} | '
            try:
                name += plugin.metadata.name if plugin.metadata and plugin.metadata.name else plugin.module.__getattribute__("__help_plugin_name__")
            except:
                name = plugin.name
            # PluginMetadata.extra['version'] preferred, then legacy or optional
            try:
                version = plugin.metadata.extra.get('version', plugin.module.__getattribute__("__help_version__")) \
                    if plugin.metadata else plugin.module.__getattribute__("__help_version__")
            except:
                version = ""
            plugin_names.append(f'{name} | {version}')
        plugin_names.sort()
        newline_char = '\n'
        result = f'已加载插件：\n{newline_char.join(plugin_names)}'
    else:
        # package name
        plugin = nonebot.get_plugin(arg)
        # try nickname/helpname
        if not plugin:
            plugin_set = nonebot.get_loaded_plugins()
            for temp_plugin in plugin_set:
                try:
                    name = temp_plugin.metadata.name if temp_plugin.metadata and temp_plugin.metadata.name \
                        else temp_plugin.module.__getattribute__("__help_plugin_name__")
                except:
                    name = temp_plugin.name
                if name == arg:
                    plugin = temp_plugin
        # not found
        if not plugin:
            result = f'{arg} 不存在或未加载，请确认输入了正确的插件名'
        else:
            results = []
            # if metadata set, use the general usage in metadata instead of legacy __usage__
            if plugin.metadata and plugin.metadata.name and plugin.metadata.usage:
                results.extend([f'{plugin.metadata.name}: {plugin.metadata.description}', plugin.metadata.usage])
            else:
                # legacy __usage__ or __doc__
                try:
                    results.extend([plugin.module.__getattribute__("__help_plugin_name__"), plugin.module.__getattribute__("__usage__")])
                except:
                    try:
                        results.extend([plugin.name, plugin.module.__doc__])
                    except AttributeError:
                        pass
            # Matcher level help, still legacy since nb2 has no Matcher metadata
            matchers = plugin.matcher
            infos = {}
            index = 1
            for matcher in matchers:
                try:
                    name = matcher.__help_name__
                except AttributeError:
                    name = None
                try:
                    help_info = matcher.__help_info__
                except AttributeError:
                    help_info = matcher.__doc__
                if name and help_info:
                    infos[f'{index}. {name}'] = help_info
                    index += 1
            if index > 1:
                results.extend(["", "序号. 命令名: 命令用途"])
                results.extend(
                    [f'{key}: {value}' for key, value in infos.items()
                     if key and value]
                )
            results = list(filter(None, results))
            result = '\n'.join(results)
    await h.finish(result)
