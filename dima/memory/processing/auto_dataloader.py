import os
import shutil
from pathlib import Path
from typing import List
import argparse
from transformers import AutoModel, AutoTokenizer

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
from langchain.schema import Document
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


def load_document(
    file_path: str,
    mapping: dict = FILE_LOADER_MAPPING,
    default_loader: BaseLoader = UnstructuredFileLoader,
) -> Document:
    # Choose loader from mapping, load default if no match found
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in mapping:
        loader_class, loader_args = mapping[ext]
        loader = loader_class(file_path, **loader_args)
    else:
        loader = default_loader(file_path)
    return loader.load()


def load_directory(path: str, silent_errors=True) -> List[Document]:
    # We don't load hidden files starting with "."
    all_files = list(Path(path).rglob("**/[!.]*"))
    results = []
    with tqdm(total=len(all_files), desc="Loading documents", ncols=80) as pbar:
        for file in all_files:
            try:
                results.extend(load_document(str(file)))
            except Exception as e:
                if silent_errors:
                    print(f"failed to load {file}")
                else:
                    raise e
            pbar.update()
    return results


def load_data_source(data_source: str) -> List[Document]:
    is_web = data_source.startswith("http")
    is_dir = os.path.isdir(data_source)
    is_file = os.path.isfile(data_source)
    docs = None
    try:
        if is_dir:
            docs = load_directory(data_source)
        elif is_file:
            docs = load_document(data_source)
        elif is_web:
            docs = load_document(data_source, WEB_LOADER_MAPPING, WebBaseLoader)
        return docs
    except Exception as e:
        error_msg = f"Failed to load your data source '{data_source}'."
        print(error_msg)
        e.args += (error_msg,)
        raise e

# def get_tokenizer(options: dict) -> Embeddings:
#     match options["model"].embedding:
#         case EMBEDDINGS.OPENAI:
#             tokenizer = tiktoken.encoding_for_model(EMBEDDINGS.OPENAI)
#         case EMBEDDINGS.HUGGINGFACE:
#             tokenizer = AutoTokenizer.from_pretrained(EMBEDDINGS.HUGGINGFACE)
#     return tokenizer

def split_docs(docs: List[Document], options: dict) -> List[Document]:
    tokenizer = AutoTokenizer.from_pretrained(options['tokenizer'])

    def length_function(text: str) -> int:
        # count chunks like the embeddings model tokenizer does
        return len(tokenizer.encode(text))

    chunk_overlap = int(options["chunk_size"] * options["chunk_overlap_size"] / 100)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=options["chunk_size"],
        chunk_overlap=chunk_overlap,
        length_function=length_function,
        separators=["\n\n", "\n", " ", ""],
    )

    splitted_docs = text_splitter.split_documents(docs)
    print(f"Loaded: {len(splitted_docs)} document chucks")
    return splitted_docs


def initialze_models():
    options_defaults = {
        'tokenizer': '',
        "model": 'chatglm-6b',
        "chunk_size": 1024,
        "chunk_overlap_size": 128,
        "max_tokens": 2048}
    return options_defaults

def main():
    parser = argparse.ArgumentParser(
    description='Start LLM and Embeddings models as a service.')
    parser.add_argument('--file_path', type=str, defalut='./DIMA/xxx.pdf')
    args = parser.parse_args()

    options = initialze_models()
    split_docs(args.file_path, options)