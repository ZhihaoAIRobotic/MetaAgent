from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


def main():
    # meta_instruction = "你是一个人工智能助手，更是人类的朋友，下面我会给出一些信息，请你根据信息和我进行轻松对话，并为我提供陪伴和情绪价值"
    model_id = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=10)
    hf = HuggingFacePipeline(pipeline=pipe)
    load_dotenv()
    st.set_page_config(page_title="Ask your PDF")
    st.header("Healthper")
    
    # upload file
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    
    # extract the text
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        # print(text)
        # split into chunks
        text_splitter = CharacterTextSplitter(
          separator="\n",
          chunk_size=100,
          chunk_overlap=3,
          length_function=len
        )
        chunks = text_splitter.split_text(text)
        # print(chunks)
        # create embeddings
        embeddings = OpenAIEmbeddings(openai_api_key="YourKey")
        knowledge_base = FAISS.from_texts(chunks, embeddings)
      
        # show user input
        user_question = st.text_input("Ask a question:")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)
            # print(docs)
            # query = meta_instruction + user_question
            prompt = PromptTemplate(input_variables=['context', 'question'], template="已知：{context}，请作为一个医护人员和朋友回答问题：{question}")
            # llm = OpenAI(openai_api_key="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")
            chain = load_qa_chain(hf, chain_type="stuff", prompt=prompt)

            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=user_question)
                print(cb)
           
            st.write(response)
    

if __name__ == '__main__':
    main()