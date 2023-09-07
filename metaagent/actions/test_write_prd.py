
from metaagent.actions.add_requirement import BossRequirement
from metaagent.information import Info
from metaagent.agents.product_manager import ProductManager
from metaagent.logs import logger


def test_write_prd():
    product_manager = ProductManager()
    requirements = "I want an AI Agent product that can help me to write and publish paper."
    prd = product_manager.handle(Info(content=requirements, cause_by='BossRequirement'))
    logger.info(requirements)
    logger.info(prd)

    # Assert the prd is not None or empty
    assert prd is not None
    assert prd != ""


test_write_prd()