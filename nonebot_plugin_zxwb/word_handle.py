import re
from typing import Any

from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
from nonebot.internal.params import Arg, ArgStr
from nonebot.params import RegexGroup
from nonebot.typing import T_State
from nonebot_plugin_alconna import AlconnaQuery, Arparma
from nonebot_plugin_alconna import Image
from nonebot_plugin_alconna import Image as alcImage
from nonebot_plugin_alconna import Match, Query, Text, UniMsg
from nonebot_plugin_alconna.uniseg.tools import reply_fetch
from nonebot_plugin_uninfo import Uninfo
from zhenxun_utils.message import MessageUtils
from zhenxun_utils.platform import PlatformUtils

from ._command import _add_matcher, _del_matcher, _update_matcher
from ._config import ScopeType, WordType, scope2int, type2int
from ._data_source import WordBankManage, get_answer, get_img_and_at_list, get_problem
from ._model import WordBank
from .exception import ImageDownloadError


@_add_matcher.handle()
async def _(
    bot: Bot,
    event: Event,
    session: Uninfo,
    state: T_State,
    message: UniMsg,
    reg_group: tuple[Any, ...] = RegexGroup(),
):
    img_list, at_list = get_img_and_at_list(message)
    user_id = session.user.id
    group_id = session.group.id if session.group else None
    if not group_id and user_id not in bot.config.superusers:
        await MessageUtils.build_message("权限不足捏...").finish(reply_to=True)
    word_scope, word_type, problem = reg_group
    if not word_scope and not group_id:
        word_scope = "私聊"
    if (
        word_scope
        and word_scope in ["全局", "私聊"]
        and user_id not in bot.config.superusers
    ):
        await MessageUtils.build_message("权限不足，无法添加该范围词条...").finish(
            reply_to=True
        )
    if word_type != "图片":
        state["problem_image"] = "YES"
    if reply := await reply_fetch(event, bot):
        if reply.msg:
            message = message[1:]
            message += Text("答") + MessageUtils.template2alc(reply.msg)  # type: ignore
        logger.debug(f"获取词条消息引用消息: {message}")
    temp_problem = message.copy()
    answer = get_answer(message.copy())
    if (not problem or not problem.strip()) and word_type != "图片":
        await MessageUtils.build_message("词条问题不能为空！").finish(reply_to=True)
    if (not answer or not answer.strip()) and not len(img_list) and not len(at_list):
        await MessageUtils.build_message("词条回答不能为空！").finish(reply_to=True)
    state["word_scope"] = word_scope
    state["word_type"] = word_type
    state["problem"] = get_problem(temp_problem)
    state["answer"] = answer.strip()
    logger.info(
        f"添加词条 范围: {word_scope} 类型: {word_type} 问题: {problem} 回答: {answer}"
    )


@_add_matcher.got("problem_image", prompt="请发送该回答设置的问题图片")
async def _(
    bot: Bot,
    session: Uninfo,
    message: UniMsg,
    word_scope: str | None = ArgStr("word_scope"),
    word_type: str | None = ArgStr("word_type"),
    problem: str | None = ArgStr("problem"),
    answer: Any = Arg("answer"),
):
    user_id = session.user.id
    group_id = session.group.id if session.group else None
    try:
        if word_type == "图片":
            problem = next(m for m in message if isinstance(m, alcImage)).url
        elif word_type == "正则" and problem:
            try:
                re.compile(problem)
            except re.error:
                await MessageUtils.build_message(
                    f"添加词条失败，正则表达式 {problem} 非法！"
                ).finish(reply_to=True)
        nickname = None
        if problem and bot.config.nickname:
            nickname = [nk for nk in bot.config.nickname if problem.startswith(nk)]
        if not problem:
            await MessageUtils.build_message("获取问题失败...").finish(reply_to=True)
        platform = PlatformUtils.get_platform(session)
        await WordBank.add_problem_answer(
            user_id,
            (
                group_id
                if group_id and (not word_scope or word_scope == "私聊")
                else "0"
            ),
            scope2int[word_scope] if word_scope else ScopeType.GROUP,
            type2int[word_type] if word_type else WordType.EXACT,
            problem,
            answer,
            nickname[0] if nickname else None,
            platform,
            session.user.id,
        )
    except ImageDownloadError:
        logger.error(f"添加词条 {problem} 错误，图片资源下载失败...")
        await MessageUtils.build_message(
            f"添加词条 {problem} 错误，图片资源下载失败..."
        ).finish()
    except Exception as e:
        if isinstance(e, FinishedException):
            await _add_matcher.finish()
        logger.error(f"添加词条 {problem} 错误...")
        await MessageUtils.build_message(
            f"添加词条 {problem if word_type != '图片' else '图片'} 发生错误！"
        ).finish(reply_to=True)
    if word_type == "图片":
        result = MessageUtils.build_message(
            ["添加词条 ", Image(url=problem), " 成功！"]
        )
    else:
        result = MessageUtils.build_message(f"添加词条 {problem} 成功！")
    await result.send()
    logger.info(f"添加词条 {problem} 成功！")


@_del_matcher.handle()
async def _(
    bot: Bot,
    session: Uninfo,
    problem: Match[str],
    index: Match[int],
    answer_id: Match[int],
    arparma: Arparma,
    all: Query[bool] = AlconnaQuery("all.value", False),
):
    if not problem.available and not index.available:
        await MessageUtils.build_message(
            "此命令之后需要跟随指定词条或id，通过“显示词条“查看"
        ).finish(reply_to=True)
    word_scope = ScopeType.GROUP if session.group else ScopeType.PRIVATE
    if all.result:
        word_scope = ScopeType.GLOBAL
    if gid := session.group.id if session.group else None:
        result, _ = await WordBankManage.delete_word(
            problem.result,
            index.result if index.available else None,
            answer_id.result if answer_id.available else None,
            gid,
            word_scope,
        )
    else:
        if session.user.id not in bot.config.superusers:
            await MessageUtils.build_message("权限不足捏...").finish(reply_to=True)
        result, _ = await WordBankManage.delete_word(
            problem.result,
            index.result if index.available else None,
            answer_id.result if answer_id.available else None,
            None,
            word_scope,
        )
    await MessageUtils.build_message(result).send(reply_to=True)
    logger.info(f"删除词条: {problem.result}")


@_update_matcher.handle()
async def _(
    bot: Bot,
    session: Uninfo,
    replace: str,
    problem: Match[str],
    index: Match[int],
    arparma: Arparma,
    all: Query[bool] = AlconnaQuery("all.value", False),
):
    if not problem.available and not index.available:
        await MessageUtils.build_message(
            "此命令之后需要跟随指定词条或id，通过“显示词条“查看"
        ).finish(reply_to=True)
    word_scope = ScopeType.GROUP if session.group else ScopeType.PRIVATE
    if all.result:
        word_scope = ScopeType.GLOBAL
    gid = session.group.id if session.group else None
    if session.user.id not in bot.config.superusers and not gid:
        await MessageUtils.build_message("权限不足捏...").finish(reply_to=True)
    result, old_problem = await WordBankManage.update_word(
        replace,
        problem.result if problem.available else "",
        index.result if index.available else None,
        gid,
        word_scope,
    )
    await MessageUtils.build_message(result).send(reply_to=True)
    logger.info(f"更新词条词条: {old_problem} -> {replace}")
