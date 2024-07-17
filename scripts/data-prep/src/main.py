import json
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from rag.indexing import (
    index_to_retriever,
    read_json_dataset,
    transform_to_document,
)
from rag.retriever import init_retriever

if __name__ == "__main__":
    print("=========================================")
    print("             DATA PREPARATION            ")
    print("=========================================")
    # Load ENV from .env
    env_file_path = os.getenv("ENV_FILE", "")
    if os.path.exists(env_file_path):
        load_dotenv(
            dotenv_path=os.getenv("ENV_FILE"),
        )

    # get from .env
    EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]
    OPENSEARCH_URL = os.environ["OPENSEARCH_URL"]
    MONGO_HOST = os.environ["MONGO_HOST"]
    MONGO_USERNAME = os.environ["MONGO_USERNAME"]
    MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]

    CONFIG_FILE_PATH = os.environ["CONFIG_FILE_PATH"]
    BULK_SIZE = os.environ["BULK_SIZE"]
    
    MONGO_URL = f"mongodb://{quote_plus(MONGO_USERNAME)}:{quote_plus(MONGO_PASSWORD)}@{MONGO_HOST}",

    # load config
    with open(CONFIG_FILE_PATH) as f:
        config_json_list = json.load(f)

    print("load model start...")
    # load embeddings model
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    print("load model finish.")
    print(f"start index data from config file: {CONFIG_FILE_PATH}")

    # get from config.json
    for config_json in config_json_list:
        if "config" in config_json:
            DATASET_PATH = config_json["config"]["dataset_path"]
            DATASET_DOC_ID = config_json["config"]["dataset_doc_id"]
            MONGO_DB_NAME = config_json["config"]["mongo_db_name"]
            MONGO_COLLECTION_NAME = config_json["config"]["mongo_collection_name"]
            OPENSEARCH_INDEX = config_json["config"]["opensearch_index"]

            print(f"[START] index data from path: {DATASET_PATH} to "
                  f"mongo_db: {MONGO_DB_NAME}, mongo_collection: {MONGO_COLLECTION_NAME}, "
                  f"opensearch_index: {OPENSEARCH_INDEX}")

            docs = read_json_dataset(DATASET_PATH)
            parsed_sub_docs, parsed_docs = transform_to_document(docs)
            retriever = init_retriever(embedding_model, OPENSEARCH_URL, OPENSEARCH_INDEX, MONGO_URL, MONGO_DB_NAME, MONGO_COLLECTION_NAME)
            index_to_retriever(retriever, parsed_sub_docs, parsed_docs, [d[DATASET_DOC_ID] for d in docs], int(BULK_SIZE))

            print(f"[FINISH] index data from path: {DATASET_PATH}")

    print("data preparation is DONE!!!")