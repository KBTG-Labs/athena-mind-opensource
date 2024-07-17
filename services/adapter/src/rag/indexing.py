import json

from langchain_core.documents import Document


def read_docs_from_json_line(path: str):
    docs = []
    with open(path) as f:
        for line in f:
            docs.append(json.loads(line))
    return docs

def transform_to_document(docs) -> tuple[list[Document], list[Document]]:
    parsed_sub_docs = []
    parsed_docs = []
    for _doc in docs:
        text = ''
        for field in _doc:
            if field != 'doc_id':
                text += field.upper() + ': ' + ", ".join(_doc[field]) + ' -- '
                for i, _text in enumerate(_doc[field]):
                    _parsed = Document(page_content=_text, metadata={"line_number": i, "field": field, "doc_id": _doc['doc_id']})
                    parsed_sub_docs.append(_parsed)
        new_doc = Document(page_content=text, metadata={"doc_id": _doc['doc_id']})
        parsed_docs.append(new_doc)
    return parsed_sub_docs, parsed_docs

def index_to_retriever(
                        retriever,
                        parsed_sub_docs: list[Document],
                        parsed_docs: list[Document],
                        id_keys: list[str]
                    ):
    retriever.vectorstore.add_documents(parsed_sub_docs, timeout=30, request_timeout=30)
    retriever.docstore.mset(list(zip(id_keys, parsed_docs)))