import chainlit as cl
import logging
import os
import yaml 
import PyPDF2

from io import BytesIO
from pathlib import Path
from langchain.globals import set_debug
from langchain_nvidia_ai_endpoints import ChatNVIDIA,NVIDIAEmbeddings
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain, ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from langchain_community.vectorstores import Milvus
from pymilvus import MilvusClient
# from langchain_milvus import MilvusVectorStore
import time

from dotenv import load_dotenv, dotenv_values 


TEXT_SPLITTER_MODEL = "intfloat/e5-large-v2"
TEXT_SPLITTER_CHUNCK_SIZE = 200
TEXT_SPLITTER_CHUNCK_OVERLAP = 50

with open(
    f"{Path(__file__).parent.resolve()}/chain_prompt_template.yaml"
) as f:
    prompt_template = yaml.safe_load(f)


CONDENSE_QUESTION_PROMPT = PromptTemplate(template=prompt_template["Prompt"]["condense_question_prompt"], input_variables=["context", "question"])

logger = logging.getLogger(__name__)
set_debug(True)

nvapi_key = os.getenv("NVIDIA_API_KEY")

embedder_document = NVIDIAEmbeddings(model="NV-Embed-QA", embed_documents="passage")
embedder_query = NVIDIAEmbeddings(model="NV-Embed-QA", embed_query="query")
text_splitter = SentenceTransformersTokenTextSplitter(
        model_name=TEXT_SPLITTER_MODEL,
        tokens_per_chunk=TEXT_SPLITTER_CHUNCK_SIZE,
        chunk_overlap=TEXT_SPLITTER_CHUNCK_OVERLAP,
    )

llm = ChatNVIDIA(model="ai-mixtral-8x7b-instruct", nvidia_api_key=nvapi_key, max_tokens=1024)


@cl.on_chat_start
async def init():    
    cl.user_session.set("embeddings", embedder_document) 
    cl.user_session.set("text_splitter", text_splitter)

    msg = await process_pdf()
    
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, output_key="answer"
    )
    cl.user_session.set("chat_history", memory)
    
    vectorstore = cl.user_session.get("vector_store")

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory = cl.user_session.get("chat_history"),
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        return_source_documents=True,
        verbose=True
    )

    cl.user_session.set("llm", llm)
    cl.user_session.set("chain", chain)
    collection_name = cl.user_session.get("collection_name")
    msg.content = f"{collection_name} processed. You can now ask questions."
    await msg.update()


def build_context(chunks):
    context = ""
    for chunk in chunks:
        context = context + "\n  Content: " + chunk.page_content + " | Title: (" + chunk.metadata["title"] + ")" 
    return context
    

def generate_answer(llm, vectorstore, prompt_template, question):
    retrieved_chunks = vectorstore.similarity_search(question)    
    context = build_context(retrieved_chunks)
    args = {"context":context, "question":question}
    prompt = prompt_template.format(**args)
    ans = llm.invoke(prompt)
    return ans.content


@cl.on_message
async def process_response(question: cl.Message):
    logger.info(f"User Question: {question.to_dict()}")

    chain: BaseConversationalRetrievalChain = cl.user_session.get("chain")
    question_dict = question.to_dict()
    question = question_dict['output']
    vectorstore = cl.user_session.get("vector_store")
    retrieved_chunks = vectorstore.similarity_search(question)    
    context = build_context(retrieved_chunks)
    args = {"context":context, "question":question}
    prompt = CONDENSE_QUESTION_PROMPT.format(**args)
    ans = llm.invoke(prompt)
    logger.info(f"Answer: {ans}")
    await cl.Message(content=ans.content).send()
    return chain


def get_milvus_client():
    # Retrieve available collections from vector store
    client = MilvusClient(uri="http://localhost:19530")
    return client


async def process_answer(answer_dict:dict)->tuple:
    question=answer_dict["question"]
    answer=answer_dict["answer"]
    logger.debug(f"Answer Dict: {answer_dict}")
    metadata=[doc.metadata for doc in answer_dict["source_documents"]]
    logger.debug(f"Metadata: {metadata}")

    return question, answer, metadata


async def process_pdf():
    embeddings = cl.user_session.get("embeddings")
    text_splitter = cl.user_session.get("text_splitter")

    files=None
    client = get_milvus_client()
    available_collections = client.list_collections()
    print(available_collections)
    collection_name = None
    while files is None:
        res = await cl.AskUserMessage(content=f"Enter a new collection name to start from scratch or choose from these available collections : {available_collections} to continue your search.", timeout=2000).send()
        print(f"Response Recieved : {res}")
        print(f"Response recieved: {res['output']}")
        if res:
            await cl.Message(
                content=f"Selected Collection: {res['output']}",
            ).send()
            collection_name = res["output"]
            cl.user_session.set('collection_name', collection_name)

        if collection_name in available_collections:
            res = await cl.AskUserMessage(content=f"Do you want to upload a new file, answere Y/N?").send()
            if res['output'] == 'no' or res['output'] == 'No' or res['output'] == 'NO' or res['output'] == 'n' or res['output'] == 'N':
                res = client.get_load_state(collection_name=collection_name)    
                vectorstore = Milvus(
                    embedding_function=embeddings,
                    collection_name=collection_name,
                    connection_args={
                        "host": "localhost", 
                        "port": "19530"},
                    drop_old = True,
                    auto_id = True
                )
                chain = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=vectorstore.as_retriever(),
                    memory = cl.user_session.get("chat_history"),
                    condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                    return_source_documents=True,
                    verbose=True
                )
                cl.user_session.set('llm', llm)
                cl.user_session.set("chain", chain)
                cl.user_session.set("vector_store", vectorstore)
                cl.user_session.set("collection_name", collection_name)
                msg = cl.Message(content=f"Ask your questions...")
                await msg.send()
                return msg
            
        files = await cl.AskFileMessage(
            content="Please upload financial statements in PDF to begin!",
            accept=["application/pdf"],
            max_size_mb=100,
            max_files=10
        ).send()

    documents = []
    for file in files:
        with open(file.path, "rb") as f:
            pdf=PyPDF2.PdfReader(f)
            file_name = file.name
            print(f"Processing File Name: {file_name}")            
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
                
            texts = text_splitter.split_text(text)
            print(f"Texts: {len(texts)}")

            for text in texts:
                metadata = {
                    "file": file_name,
                    "title": file_name
                }
                documents.append(Document(page_content=text, metadata=metadata))

    print(f"{len(documents)} documents created.")

    collection_name=cl.user_session.get('collection_name')
    msg = cl.Message(content=f"Processing files...")
    await msg.send()
    
    embeddings = cl.user_session.get("embeddings")
    vectorstore = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={
            "host": "localhost", 
            "port": "19530"},
        drop_old = True,
        auto_id = True
    )
    docs_indxed = vectorstore.add_documents(documents)

    print(f"{collection_name}")
    print(f"Indexed Docs = {docs_indxed}")
    cl.user_session.set("vector_store", vectorstore)
    cl.user_session.set("collection_name", collection_name)

    return msg