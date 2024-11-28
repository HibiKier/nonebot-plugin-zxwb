import nonebot
from nonebot import logger
from tortoise import Tortoise
from tortoise.connection import connections
from tortoise.models import Model as Model_

from ._config import ZxwbConfig, data_dir

driver = nonebot.get_driver()

MODELS: list[str] = []


class DbConnectError(Exception):
    """
    数据库连接错误
    """

    pass


class Model(Model_):
    """
    自动添加模块

    Args:
        Model_: Model
    """

    def __init_subclass__(cls, **kwargs):
        MODELS.append(cls.__module__)


@driver.on_startup
async def _():
    if not ZxwbConfig.zxwb_db_url:
        db_file = data_dir / "db" / "zxwb.db"
        db_file.parent.mkdir(parents=True, exist_ok=True)
        ZxwbConfig.zxwb_db_url = f"sqlite:{db_file.absolute()}"
        logger.info(f"未配置ZXWB数据库连接，使用默认连接: sqlite:{db_file.absolute()}")
    try:
        await Tortoise.init(
            db_url=ZxwbConfig.zxwb_db_url,
            modules={"models": MODELS},
            timezone="Asia/Shanghai",
        )
        await Tortoise.generate_schemas()
        logger.info("ZXWB数据库加载完成!")
    except Exception as e:
        raise DbConnectError(f"ZXWB数据库连接错误... e:{e}") from e


@driver.on_shutdown
async def disconnect():
    await connections.close_all()
