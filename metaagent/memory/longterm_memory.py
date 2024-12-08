from typing import List, Union, TypeVar
from collections.abc import Iterable

from metaagent.information import Info
from metaagent.memory.vector_store.chroma import ChromaVS
from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.memory.processing.auto_dataloader import Dataloader
import langid
import re
from metaagent.memory.processing.text_splitter_chinese import Chinese_Text_Splitter, textsplitter_with_overlap

from metaagent.memory.processing.text_splitter_english import English_Text_Splitter

T = TypeVar('T')


def check_language(string: str) -> str:
    """Check language
    :return zh: Chinese, en:English,
    """
    new_string = re.sub(r'[0-9]+', '', string)  # remove numbers
    return langid.classify(new_string)[0]


class LongTermMemory():
    """
    The Long-term memory for Roles
    - recover memory when it staruped
    - update memory when it changed
    """

    def __init__(self, workid, embedding_model: str = None, ApiKey: str = None):
        '''
        Args:
            workid: the id of the workflow
            embedding_model: the name of the embedding model to use, now support ['OpenAI', 'huggingface'].
            ApiKey: the api key to use for the embedding model.
        '''
        self.workid = workid
        self.memory_storage = ChromaVS(workid, embedding_model, ApiKey)
        self.memory_storage.create_load_collection()

    def remember_infos(self, message: Info):
        """
        remember the message into memory_storage
        """
        metadata = [{"memory_type": 'Info'}, {"agentid": message.agent_id}]  # document type, agent id
        self.memory_storage.add_texts(message.content, metadatas=metadata)

    def remember_shortterm_memory(self, shortterm_memory: ShortTermMemory):
        """
        remember the short-term memory(stm) 
        """
        metadata = [{"memory_type": 'Info'}, {"agentid": shortterm_memory.agent_id}]
        for message in shortterm_memory:
            self.memory_storage.add_texts(message.content, metadatas=metadata)

    def remember_knowledge(self, documents: Union[T, List[T]], namespace: str = None):
        """
        remember the message into memory_storage
        """
        metadata = [{"memory_type": 'Knowledge'}, {"namespace": namespace}]
        if isinstance(documents, Iterable):
            for doc in documents:
                dataloader = Dataloader()
                texts = dataloader(doc)
                if check_language(texts) == 'zh':
                    split_sentence = Chinese_Text_Splitter()
                    sentences = split_sentence(texts, criterion='coarse')
                    text_list = textsplitter_with_overlap(sentences)
                elif check_language(texts) == 'en':
                    split_sentence = English_Text_Splitter()
                    text_list = split_sentence(texts)
                else:
                    split_sentence = English_Text_Splitter()
                    text_list = split_sentence(texts)
                for text in text_list:
                    self.memory_storage.add_texts(text, metadatas=metadata)

    def recall_infos(self, related_text: str = '', agentid: str = '', k=0) -> List[str]:
        """
        remember the most similar k memories from observed Messages, return all when k=0
        """
        metadata = [{"memory_type": 'Info'}, {"agentid": agentid}]  # document type, agent id
        documents = self.memory_storage.query_text(related_text, top_k=k, metadata=metadata)
        return documents

    def recall_knowledge(self, observed, namespace: str = None, k=0) -> List[str]:
        """
        remember the most similar k memories from observed Messages, return all when k=0
            1. remember the short-term memory(stm) news
            2. integrate the stm news with ltm(long-term memory) news
        """
        if namespace is None:
            metadata = [{"memory_type": 'Knowledge'}]
        else:
            metadata = [{"memory_type": 'Knowledge'}, {"namespace": namespace}]
        
        documents = self.memory_storage.query_text(observed, top_k=k, metadata=metadata)
        return documents
    
    def forget(self, message):
        '''
        delete specific content in memory_storage
        '''
        # TODO delete message in memory_storage

    def clear(self):
        '''
        clear all content in memory_storage
        '''
        # TODO delete message in memory_storage

