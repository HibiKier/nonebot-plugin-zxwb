from nonebot import logger, on_message
from nonebot.typing import T_State
from nonebot_plugin_uninfo import Uninfo

from ._model import WordBank
from ._rule import check

_matcher = on_message(priority=6, block=True, rule=check)


@_matcher.handle()
async def _(session: Uninfo, state: T_State):
    if problem := state.get("problem"):
        gid = session.group.id if session.group else None
        if result := await WordBank.get_answer(gid, problem):
            await result.send()
            logger.info(f"触发词条 {problem}")
