from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.chains import RetrievalQA


def QA(file_path, query, is_pdf=False):
    # 加载文件夹中的所有txt类型的文件
    if is_pdf:
        loader = PyPDFLoader(file_path)
    else:
        loader = DirectoryLoader(file_path, glob='**/*.txt')
    # 将数据转成 document 对象，每个文件会作为一个 document
    documents = loader.load()

    # 初始化加载器
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    # 切割加载的 document
    split_docs = text_splitter.split_documents(documents)

    # 初始化 openai 的 embeddings 对象
    embeddings = OpenAIEmbeddings()
    persist_directory = 'db'
    # 将 document 通过 openai 的 embeddings 对象计算 embedding 向量信息并存入 Chroma 向量数据库，用于后续匹配查询
    docsearch = Chroma.from_documents(split_docs, embeddings, persist_directory=persist_directory)
    docsearch.persist()

    docs = docsearch.similarity_search(query, include_metadata=True)
    # 创建问答对象
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.as_retriever(), return_source_documents=True)
    # 进行问答
    qa.run(input_documents=docs, question=query)


def demo():
    file_path = '/home/wy/books'
    query = "小说讲了什么的故事?"
    QA(file_path, query)