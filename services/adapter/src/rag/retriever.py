from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.storage.mongodb import MongoDBStore
from langchain_community.vectorstores.opensearch_vector_search import (
    OpenSearchVectorSearch,
)
from langchain_core.embeddings import Embeddings

id_key = 'doc_id'

def init_retriever(
    embedding_model: str | Embeddings, 
    opensearch_url:str, 
    opensearch_index:str,
    mongo_url: str, 
    mongo_db_name:str, 
    mongo_collection_name:str,
) -> MultiVectorRetriever:

    if issubclass(type(embedding_model), Embeddings):
        embeddings = embedding_model
    elif isinstance(embedding_model, str):
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    else:
        # TODO Add exception detail
        raise TypeError
        
    docsearch = OpenSearchVectorSearch(
        opensearch_url,
        opensearch_index,
        embeddings
    )
    store = MongoDBStore(mongo_url, db_name=mongo_db_name, collection_name=mongo_collection_name)
    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=docsearch,
        docstore=store,
        id_key=id_key,
    )
    
    return retriever
