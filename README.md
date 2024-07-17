# Athena-mind-opensource

Athena-mind-opensource is a chatbot framework designed to save you from building a chatbot from scratch.

## System Diagram
![AthenaMindSystemDiagram](.github/AthenaMind_Diagram.png?raw=true)

## Key Features 
* __Versatile Adapter Support for Multiple Use Cases__
  * Ready-to-use RAG template to quickly set up a pre-defined RAG with your documents
  * Fully customizable using Langchain for more complex processes
* __Intelligent Routing Between Adapters__
  * Seamless routing powered by LLM using only adapter names and roles
* __Production-Ready LLM & Vector Model Deployment__
  * Ready for production deployment along with message queues for batch processing using Kafka
* __User-Friendly Interface with Chainlit__
  * Communicates with REST API and provides a simple UI for chatting
* __Efficient Data Preparation__
  * Prepares data from various formats for seamless processing and use by the RAG adapter created by the template

## Prerequisites
### Hardware Requirements
| LLM                        | CPU | Memory | GPU | GPU Memory |
|----------------------------|-----|--------|-----|------------|
| Gemini (Cloud Service)     | 4   | 16GB   | -   | -          |
| Hugging Face (Self-Hosted) | 8   | 32GB   | 1   | 16 GB      |


### Software Requirements
Ensure you have installed the following prerequisites on your development machine
* Docker
* Docker Compose 2.20.3+
* MongoDB Compass (optional)
* [Gemini API Key](https://aistudio.google.com/app/apikey)
* [Hugging Face Access Token](https://huggingface.co/docs/hub/en/security-tokens)

## Getting Started
The provided datasource refers to information about __KBank’s bank account__ from the following links:
* [บัญชีเงินฝากออมทรัพย์ K-eSavings](https://www.kasikornbank.com/th/personal/digital-banking/pages/k-esavings-account.aspx)
* [เปิดบัญชีเงินฝากออมทรัพย์ K-eSavings ผ่าน K PLUS](https://www.kasikornbank.com/th/personal/Digital-banking/Pages/k-esavings-account-opening-have-kplus.aspx)
* [ขั้นตอนการเปิดบัญชีออนไลน์ K-eSavings สำหรับลูกค้าใหม่](https://www.kasikornbank.com/th/personal/Digital-banking/Pages/k-esavings-account-opening-have-no-kplus.aspx)
* [บัญชีเงินฝากออมทรัพย์](https://www.kasikornbank.com/th/personal/account/pages/savings.aspx)
* [บัญชีเงินฝากประจำ](https://www.kasikornbank.com/th/personal/account/pages/fixed.aspx)
* [บัญชีเงินฝากกระแสรายวัน](https://www.kasikornbank.com/th/personal/account/pages/current.aspx)
* [บัญชีเงินฝากเงินตราต่างประเทศ](https://www.kasikornbank.com/th/personal/account/pages/foreign-currency.aspx)

Here are the instructions to run with the sample data source provided in the `data` folder.

1. Set up your `.env` file with your specific values.
    ```dotenv
    # Kafka config
    # KAFKA_EXPOSE_PORT MUST NOT be set to `9092`
    KAFKA_EXPOSE_PORT=9093
    
    # Mongo config
    MONGO_INITDB_ROOT_USERNAME= #REQUIRED
    MONGO_INITDB_ROOT_PASSWORD= #REQUIRED
    MONGO_EXPOSE_PORT=27017
    
    # Opensearch config
    OPENSEARCH_DASHBOARD_EXPOSE_PORT=5601
    
    # NLU
    NLU_SERVICE_EXPOSE_PORT=8901
    
    # Adapter Service
    ADAPTER_SERVICE_EXPOSE_PORT=8900
    
    # Gemini
    GEMINI_API_KEY= #REQUIRED
    
    ##########################
    # OpenTelemetry
    # To enable telemetry, you need to modify the `docker-compose.yml` file to configure the tracing UI first.
    # If you are using an example, here is a sample configuration.
    
    # ENABLE_TELEMETRY=True
    # TELEMETRY_COLLECTOR_ENDPOINT="http://jaeger:14268/api/traces?format=jaeger.thrift"
    ##########################
    ENABLE_TELEMETRY=False
    TELEMETRY_COLLECTOR_ENDPOINT=
    ```
   
    > [!IMPORTANT]
    > Ensure that __KAFKA_EXPOSE_PORT__ is not configured as 9092
   
2. Running service
   ```shell
   docker compose up --build -d
   ```
   Wait until data-prep is ready, then you can access the UI chatbot by opening [http://localhost:8901](http://localhost:8901)
   ![AthenaMindChainlit](.github/AthenaMind_Chainlit.png?raw=true)

3. Sample command for using Docker Compose.
* Check service health
  ```shell
  docker compose ps
  ```
* View service logs
  ```shell
  # specific service
  docker compose logs {{service name}}
  # all service
  docker compose logs -f
  ```
  > [!NOTE]
  > {{service name}} obtained from the service name in `docker-compose.yml`.


* Stop all services
  ```shell
  docker compose down
  ```

## Project structure
* `data` : Data source for RAG
* `deployments` : Infra service deployments
* `scripts` : Helper scripts that include functionalities such as:
  * Data preparation
  * Create kafka topic
* `services` : All services provided by athena-mind-opensource.

## Customized data source
Prepare your data in `data` folder with the following details:
1. `data/config.json`

   ```json
   [
       {
           "adapter": "web_account",
           "name": "Account Expert",
           "role": "Answer the question about four accounts: FCD (Foreign Currency Deposit), K-eSaving and other types of accounts",
           "type": "rag",
           "host": "service-adapter:8900",
           "config": {
               "dataset_path": "data/web_account/data/all_data.jsonl",
               "dataset_doc_id": "doc_id",
               "mongo_db_name": "athena-web-account",
               "mongo_collection_name": "testing",
               "opensearch_index": "athena-web-account",
               "prompt": {
                   "dir": "data/web_account/prompt",
                   "query_generate_prompt": "query_generation_prompt.txt",
                   "qa_prompt": "qa_prompt.txt",
                   "response_control_prompt": "rc_prompt.txt"
               }
           }
       },
       {
           "adapter": "general_handler",
           "name": "General Handler",
           "role": "Answer any questions about others",
           "type": "custom",
           "host": "service-adapter:8900"
       }
   ]
   ```
   __Fields Description:__
   * __adapter__ - Must be the name of folder inside `data` folder.
   * __name__ - Name of adapter
   * __role__ - Short description about role of chatbot 
   * __type__
     * custom
     * rag
   * __host__ - Adapter endpoint
   * __config__
     * dataset_path - Path to refer your dataset
     * dataset_doc_id - Document key name
     * mongo_db_name - Name of db in mongo
     * mongo_collection_name - Name of collection in mongo
     * opensearch_index - Name of index in opensearch
     * prompt
       * dir - Directory that store prompt
       * query_generate_prompt - File name of prompt for query generation
       * qa_prompt - File name of prompt for question and answer prompt
       * response_control_prompt - File name of prompt for response control


2. `data/{{adapter}}/data/{{name}}.jsonl`
   > [!CAUTION]
   > {{adapter}} - __MUST MATCH__ with field __adapter__ in `data/config.json`

   ```json
   {
     "doc_id": "method_with_kplus",
     "url": [
       "https://www.kasikornbank.com/th/personal/Digital-banking/Pages/k-esavings-account-opening-have-kplus.aspx"
     ],
     "title": [
       "วิธีเปิดบัญชีออนไลน์ K-eSavings"
     ],
     "description": [
       "เปิดปุ๊บ ใช้งานได้ปั๊บ ภายใน 5 ขั้นตอน",
       "1. เข้าสู่ระบบ และเลือก \"บริการอื่น\" เพื่อเปิดบัญชีเงินฝาก",
       "2. เลือก \"เปิดบัญชีเงินฝาก\" ในบริการอื่น และเลือก \"เปิดบัญชีใหม่\"",
       "3. อ่านข้อตกลงและเงื่อนไข กรอกข้อมูลให้ครบถ้วน และเลือก \"ถัดไป\"",
       "4. ตรวจสอบข้อมูลอีกครั้งหลังจากกรอกข้อมูล หากถูกต้องแล้วเลือก \"ยืนยัน\"",
       "5. ลูกค้าจะได้รับรายละเอียดบัญชีผ่านทาง Feed SMS และอีเมลที่ได้ลงทะเบียนไว้กับธนาคาร"
     ]
   }
   ```
   __JSON Object__ can be customized, but it should include the following details: 
   * __Document Key__ [string] - The field name __MUST MATCH__ the value of the key ___config.dataset_doc_id___ from `data/config.json` (i.e., doc_id)
   * __Data Fields__ [list of string] - Can have more than one fields (i.e., url, title, description)


3. Re-create service
   ```shell
   docker compose up --build -d
   ```
   
## Development
If you want to customize the service for a specific case, please refer to the instruction below.
* [Create adapter using predefined RAG](services/adapter/README.md#creating-an-adapter-using-predefined-rag)
* [Create your customized adapter](services/adapter/README.md#creating-your-customized-adapter)
* [Change the Vector Model](services/vector/README.md#model-update)
* [Change the LLM Model](services/llm/README.md#model-update-for-hugging-face)

## References
* [Chainlit](https://docs.chainlit.io/get-started/overview) is an open-source Python package to build production ready Conversational AI.
* [LangGraph](https://langchain-ai.github.io/langgraph/) is a library within the LangChain ecosystem that provides a framework for defining, coordinating, and executing multiple LLM agents (or chains) in a structured and efficient manner.
* [LangChain](https://python.langchain.com/v0.2/docs/introduction/) is a framework for developing applications powered by large language models (LLMs).
* [LangServe](https://python.langchain.com/v0.2/docs/langserve/) is a Python framework that helps developers deploy LangChain runnable and chains as REST APIs

## License
The project is licensed under the [Apache License 2.0](LICENSE).
