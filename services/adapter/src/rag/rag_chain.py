from langchain.chains import create_retrieval_chain
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough


def read_prompt(path: str) -> str:
    with open(path) as f:
        return "\n".join(f.readlines())
        
def init_rag_chain(
        retriever: BaseRetriever, 
        llm: BaseLanguageModel, 
        qg_prompt_path:str, 
        qa_prompt_path:str, 
        rc_prompt_path:str
    ):
    contextualize_q_system_prompt = read_prompt(qg_prompt_path)
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("messages")
        ]
    )
    history_aware_retriever = contextualize_q_prompt | llm | StrOutputParser() | retriever
    qa_system_prompt = read_prompt(qa_prompt_path)
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("messages")
        ]
    )

    def format_docs(inputs: dict) -> str:
        for d in [doc.page_content.split("--")[0] for doc in inputs["context"][:3]]:
            print(d)
        result = "\n\n".join(
            doc.page_content for doc in inputs["context"][:3]
        )
        return result[:30000]
    
    question_answer_chain = (
        RunnablePassthrough.assign(**{"context": format_docs}).with_config(
            run_name="format_inputs"
        )
        | qa_prompt
        | llm
        | StrOutputParser()
    ).with_config(run_name="stuff_documents_chain")
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    rc_prompt = ChatPromptTemplate.from_template(read_prompt(rc_prompt_path))
    output_parser = StrOutputParser()
    final_chain = rag_chain | rc_prompt | llm | output_parser
    return final_chain