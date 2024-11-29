from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_localstore")

from ._config import Config  # noqa: E402

__plugin_meta__ = PluginMetadata(
    name="ZXWB词库问答",
    description="小真寻的词库问答，对群组/私聊/全局进行区分，支持 精准/模糊/正则/图片 匹配",
    usage=r"""
    对指定问题的随机回答，对相同问题可以设置多个不同回答
    删除词条后每个词条的id可能会变化，请查看后再删除
    更推荐使用id方式删除
    问题回答支持的类型：at, image
    查看词条命令：群聊时为 群词条+全局词条，私聊时为 私聊词条+全局词条
    添加词条正则：添加词条(模糊|正则|图片)?问\s*?(\S*\s?\S*)\s*?答\s?(\S*)
    正则问可以通过$1类推()捕获的组
    注意：可以通过引用来提供回答， 如：（引用）添加词条问你好
    指令：
        添加词条 ?[模糊|正则|图片]问...答...：添加问答词条，可重复添加相同问题的不同回答
            示例:
                添加词条问你好答你也好
                添加词条图片问答看看涩图
        删除词条 ?[问题] ?[序号] ?[回答序号]：删除指定词条指定或全部回答
            示例:
                删除词条 谁是萝莉           : 删除文字是 谁是萝莉 的词条
                删除词条 --id 2            : 删除序号为2的词条
                删除词条 谁是萝莉 --aid 2   : 删除 谁是萝莉 词条的第2个回答
                删除词条 --id 2 --aid 2    : 删除序号为2词条的第2个回答
        修改词条 [替换文字] ?[旧词条文字] ?[序号]：修改词条问题
            示例:
                修改词条 谁是萝莉 谁是萝莉啊？ : 将词条 谁是萝莉 修改为 谁是萝莉啊？
                修改词条 谁是萝莉 --id 2     : 将序号为2的词条修改为 谁是萝莉
        查看词条 ?[问题] ?[序号]：查看全部词条或对应词条回答
            示例:
                查看词条:
                    (在群组中使用时): 查看当前群组词条和全局词条
                    (在私聊中使用时): 查看当前私聊词条和全局词条
                查看词条 谁是萝莉   : 查看词条 谁是萝莉 的全部回答
                查看词条 --id 2    : 查看词条序号为2的全部回答
                查看词条 谁是萝莉 --all: 查看全局词条 谁是萝莉 的全部回答
                查看词条 --id 2 --all: 查看全局词条序号为2的全部回答
        查看词条:
            (在群组中使用时): 查看当前群组词条和全局词条
            (在私聊中使用时): 查看当前私聊词条和全局词条
            查看词条 谁是萝莉   : 查看词条 谁是萝莉 的全部回答
            查看词条 --id 2    : 查看词条序号为2的全部回答
            查看词条 谁是萝莉 --all: 查看全局词条 谁是萝莉 的全部回答
            查看词条 --id 2 --all: 查看全局词条序号为2的全部回答

    超级用户额外指令
        在私聊中超级用户额外设置
        指令：
            (全局|私聊)?添加词条\s*?(模糊|正则|图片)?问\s*?(\S*\s?\S*)\s*?答\s?(\S*)：添加问答词条，可重复添加相同问题的不同回答
            全局添加词条
            私聊添加词条
            （私聊情况下）删除词条: 删除私聊词条
            （私聊情况下）修改词条: 修改私聊词条
            通过添加参数 --all才指定全局词条
            示例:
                删除词条 --id 2 --all: 删除全局词条中序号为2的词条
            用法与普通用法相同
    """,
    type="application",
    homepage="https://github.com/HibiKier/nonebot-plugin-zxwb",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    extra={"author": "HibiKier"},
)

from .message_handle import *  # noqa: E402, F403
from .read_word_bank import *  # noqa: E402, F403
from .word_handle import *  # noqa: E402, F403
