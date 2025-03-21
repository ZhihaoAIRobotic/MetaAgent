import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from metaagent.memory.processing.auto_dataloader import DataLoader
from metaagent.memory.processing.web2markdown import web2md
from metaagent.memory.processing.pdf2markdown import pdf2md


if __name__ == "__main__":
    dataloader = DataLoader()
    # web chunk
    data_splitted = dataloader.split_data_from_source("https://github.com/ZhihaoAIRobotic/MetaAgent")
    print(type(data_splitted))
    print(len(data_splitted))

    # pdf chunk
    text_content, images = pdf2md("/home/lzh/DeepSeek从入门到精通-清华")
    data_splitted = dataloader.split_data_from_str(text_content, True)
    print(type(data_splitted))
    print(len(data_splitted))
    print(data_splitted)
