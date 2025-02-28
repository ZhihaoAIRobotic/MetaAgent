import os
from pathlib import Path
from typing import List
import tiktoken
from abc import ABC
from langchain_community.document_loaders import (
    EverNoteLoader,
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
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from tqdm import tqdm


FILE_LOADER_MAPPING = {
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


class DataLoader():
    def __init__(self, chunk_size=1024, chunk_overlap=32, headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
    ]):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.headers_to_split_on = headers_to_split_on

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

    def split_data_from_source(self, file_path: str):
        ext = "." + file_path.rsplit(".", 1)[-1]
        docs = self.load_data_source(file_path)

        if ext == ".md":
            text_splitter = MarkdownHeaderTextSplitter(self.headers_to_split_on)
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

        splitted_docs = text_splitter.split_documents(docs)

        return splitted_docs
    
    def split_data_from_str(self, content: str, is_markdown: bool):
        if is_markdown:
            text_splitter = MarkdownHeaderTextSplitter(self.headers_to_split_on)
        else:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        return text_splitter.split_text(content)



def main():
    dataloader = DataLoader()
    docs = dataloader.split_data_from_source('https://github.com/ZhihaoAIRobotic/MetaAgent')
    print(type(docs))
    # print(docs)


if __name__ == '__main__':
    main()
