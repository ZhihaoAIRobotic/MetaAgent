
from metaagent.actions.add_requirement import BossRequirement
from metaagent.information import Info
from metaagent.agents.product_manager import ProductManager
from metaagent.logs import logger


def test_write_prd():
    product_manager = ProductManager()
    requirements = "开发一个基于大语言模型与私有知识库的搜索引擎，希望可以基于大语言模型进行搜索总结"
    prd = product_manager.handle(Info(content=requirements, cause_by='BossRequirement'))
    logger.info(requirements)
    logger.info(prd)

    # Assert the prd is not None or empty
    assert prd is not None
    assert prd != ""


test_write_prd()