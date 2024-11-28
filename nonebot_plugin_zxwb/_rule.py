from io import BytesIO

import imagehash
from PIL import Image
from nonebot import logger
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot_plugin_uninfo import Uninfo
from zhenxun_utils.http_utils import AsyncHttpx
from nonebot_plugin_alconna import At, Text, UniMsg

from ._model import WordBank
from ._data_source import get_img_and_at_list


async def check(
    bot: Bot,
    event: Event,
    message: UniMsg,
    session: Uninfo,
    state: T_State,
) -> bool:
    text = message.extract_plain_text().strip()
    img_list, at_list = get_img_and_at_list(message)
    problem = text
    if not text and len(img_list) == 1:
        try:
            r = await AsyncHttpx.get(img_list[0])
            problem = str(imagehash.average_hash(Image.open(BytesIO(r.content))))
        except Exception as e:
            logger.warning(f"词条获取图片失败 {type(e)}:{e}...")
    if at_list:
        temp = ""
        # TODO: 支持更多消息类型
        for msg in message:
            if isinstance(msg, At):
                temp += f"[at:{msg.target}]"
            elif isinstance(msg, Text):
                temp += msg.text
        problem = temp
    if event.is_tome() and bot.config.nickname:
        if isinstance(message[0], At) and message[0].target == bot.self_id:
            problem = f"[at:{bot.self_id}]{problem}"
        elif problem and bot.config.nickname:
            nickname = [nk for nk in bot.config.nickname if str(message).startswith(nk)]
            problem = nickname[0] + problem if nickname else problem
    group_id = session.group.id if session.group else None
    if problem and (await WordBank.check_problem(group_id, problem) is not None):
        state["problem"] = problem  # type: ignore
        return True
    return False
