import os
import shutil
from pathlib import Path
from typing import List
import argparse
import tiktoken
from abc import ABC, abstractmethod
from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    GitLoader,
    NotebookLoader,
    OnlinePDFLoader,
    PDFMinerLoader,
    PythonLoader,
    TextLoader,
    UnstructuredEPubLoader,
    UnstructuredFileLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
)
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm


FILE_LOADER_MAPPING = {
    ".csv": (CSVLoader, {"encoding": "utf-8"}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PDFMinerLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    ".ipynb": (NotebookLoader, {}),
    ".py": (PythonLoader, {}),
    # Add more mappings for other file extensions and loaders as needed
}

WEB_LOADER_MAPPING = {
    ".pdf": (OnlinePDFLoader, {}),
}


class Dataloader(ABC):
    def __init__(self, chunk_size=1024, chunk_overlap=32, tokenizer=tiktoken.get_encoding('cl100k_base')):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tokenizer

    def load_directory(self, path: str, silent_errors=True):
        # We don't load hidden files starting with "."
        all_files = list(Path(path).rglob("**/[!.]*"))
        results = []
        with tqdm(total=len(all_files), desc="Loading documents", ncols=80) as pbar:
            for file in all_files:
                try:
                    results.extend(self.load_document(str(file)))
                except Exception as e:
                    if silent_errors:
                        print(f"failed to load {file}")
                    else:
                        raise e
                pbar.update()
        return results

    def load_document(self, file_path: str, mapping: dict = FILE_LOADER_MAPPING, default_loader: BaseLoader = UnstructuredFileLoader):
        # Choose loader from mapping, load default if no match found
        ext = "." + file_path.rsplit(".", 1)[-1]
        if ext in mapping:
            loader_class, loader_args = mapping[ext]
            loader = loader_class(file_path, **loader_args)
        else:
            loader = default_loader(file_path)
        return loader.load()

    def load_data_source(self, data_source: str):
        is_web = data_source.startswith("http")
        is_dir = os.path.isdir(data_source)
        is_file = os.path.isfile(data_source)
        docs = None
        try:
            if is_dir:
                docs = self.load_directory(data_source)
            elif is_file:
                docs = self.load_document(data_source)
            elif is_web:
                docs = self.load_document(data_source, WEB_LOADER_MAPPING, WebBaseLoader)
            return docs
        except Exception as e:
            error_msg = f"Failed to load your data source '{data_source}'."
            print(error_msg)
            e.args += (error_msg,)
            raise e

    def __call__(self, file_path: str):
        docs = self.load_data_source(file_path)
        doc_text = ""

        def length_function(text: str) -> int:
            # count chunks like the embeddings model tokenizer does
            return len(self.tokenizer.encode(text, disallowed_special=()))

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=length_function,
            separators=["\n\n", "\n", " ", ""],
        )

        splitted_docs = text_splitter.split_documents(docs)
        doc_text_list = [docs.page_content for docs in splitted_docs]
        for i in doc_text_list:
            doc_text += i

        return doc_text


def main():
    dataloader = Dataloader()
    docs = dataloader('https://github.com/ZhihaoAIRobotic/MetaAgent')
    print(type(docs))
    print(docs)


if __name__ == '__main__':
    main()
