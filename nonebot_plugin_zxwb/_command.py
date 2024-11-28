from nonebot import on_regex
from nonebot.permission import SUPERUSER
from nonebot_plugin_uninfo.permission import ADMIN
from nonebot_plugin_alconna import Args, Option, Alconna, on_alconna, store_true

_add_matcher = on_regex(
    r"^(全局|私聊)?添加词条\s*?(模糊|正则|图片)?问(\S*\s?\S*)",
    priority=5,
    block=True,
    permission=ADMIN() | SUPERUSER,
)


_del_matcher = on_alconna(
    Alconna(
        "删除词条",
        Args["problem?", str],
        Option("--all", action=store_true, help_text="所有词条"),
        Option("--id", Args["index", int], help_text="下标id"),
        Option("--aid", Args["answer_id", int], help_text="回答下标id"),
    ),
    priority=5,
    block=True,
    permission=ADMIN() | SUPERUSER,
)


_update_matcher = on_alconna(
    Alconna(
        "修改词条",
        Args["replace", str]["problem?", str],
        Option("--id", Args["index", int], help_text="词条id"),
        Option("--all", action=store_true, help_text="全局词条"),
    ),
    priority=5,
    block=True,
    permission=ADMIN() | SUPERUSER,
)
