from nonebot import logger
from nonebot_plugin_uninfo import Uninfo
from zhenxun_utils.message import MessageUtils
from nonebot_plugin_alconna import (
    Args,
    Match,
    Query,
    Option,
    Alconna,
    AlconnaQuery,
    on_alconna,
    store_true,
)

from ._model import WordBank
from ._config import ScopeType
from ._data_source import WordBankManage

_show_matcher = on_alconna(
    Alconna(
        "显示词条",
        Args["problem?", str],
        Option("-g|--group", Args["gid", str], help_text="群组id"),
        Option("--id", Args["index", int], help_text="词条id"),
        Option("--all", action=store_true, help_text="全局词条"),
    ),
    aliases={"查看词条"},
    priority=5,
    block=True,
)


@_show_matcher.handle()
async def _(
    session: Uninfo,
    problem: Match[str],
    index: Match[int],
    gid: Match[str],
    all: Query[bool] = AlconnaQuery("all.value", False),
):
    group_id = session.group.id if session.group else None
    word_scope = ScopeType.GROUP if group_id else ScopeType.PRIVATE
    if all.result:
        word_scope = ScopeType.GLOBAL
    if gid.available:
        group_id = gid.result
    if problem.available:
        if index.available and (
            index.result < 0
            or index.result > len(await WordBank.get_problem_by_scope(word_scope))
        ):
            await MessageUtils.build_message("id必须在范围内...").finish(reply_to=True)
        result = await WordBankManage.show_word(
            problem.result,
            index.result if index.available else None,
            group_id,
            word_scope,
        )
    else:
        result = await WordBankManage.show_word(
            None, index.result if index.available else None, group_id, word_scope
        )
    await result.send()
    logger.info(
        f"查看词条回答: {problem.result if problem.available else index.result}"
    )
