# athena-mind-nlu

The athena-mind-nlu project is designed to provide user-friendly interface and seamlessly route to adapter based on user query and conversation history.

## Overview

### Objective
   The primary objective of the athena-mind-nlu project is to serve a user interface using chainlit and routing to the optimal adapter.

### Key Features
- **Intelligent Routing Between Adapters**: Seamless routing powered by LLM using only adapter names and roles
- **Adapter Selecter**: Choose the optimal adapter to handle the current user query, powered by Language Learning Model (LLM).
- **User-Friendly Interface with Chainlit**: Communicates with REST API and provides a simple UI for chatting.
- **Ease of Deployment**: Integrates with DevOps API for streamlined deployment processes using Makefile and Docker Compose.
- **Custom Configuration**: Provides extensive configuration options for logging, and message queue (MQ).

## Getting Started

### Prerequisites

- Python Version
    
    Ensure you have Python 3.10 installed. You can download it from the [official Python website](https://www.python.org/downloads/).

- pip

    pip is the package installer for Python and is included with Python 3.10. To verify if pip is installed, you can run the following command:

    ```bash
    pip --version
    ```

    If pip is not installed, you can install it by following the official [pip installation guide](https://pip.pypa.io/en/stable/installation/).

- Kafka Cluster

    A running Kafka cluster is required for message queuing.
    Also ensure that you have aligned the Kafka server address and the necessary configuration details in the .env file to connect to the Kafka cluster.

- athena-mind-adapter

    A running athena-mind-adapter is required for routing message to the selected adapter by user intent.

### Installation

1. Open the Terminal 
2. Navigate to the Root Directory
3. (Optional) Create a Python Virtual Environment
    ```
    python -m venv venv
    ```
4. (Optional) Activate the Virtual Environment
    - For MacOS or Linux
        ```
        source venv/bin/activate
        ```
    - For Windows
        ```
        .\venv\Scripts\activate
        ```
5. Install Project Dependencies
    ```
    make app-install
    ```

### Run Project Locally ([Installation Required](#installation))

1. Open the Terminal 
2. Navigate to the Root Directory
3. (Optional) Activate the Virtual Environment
    - For MacOS or Linux
        ```
        source venv/bin/activate
        ```
    - For Windows
        ```
        .\venv\Scripts\activate
        ```
4. Run Project
    ```
    make app-start
    ```

### Run Unit Tests Locally ([Installation Required](#installation))

1. Open the Terminal 
2. Navigate to the Root Directory
3. (Optional) Activate the Virtual Environment
    - For MacOS or Linux
        ```
        source venv/bin/activate
        ```
    - For Windows
        ```
        .\venv\Scripts\activate
        ```
4. Run Unit Tests
    ```
    make app-test
    ```


## Development

1. **Environment Configuration**

    To configure the environment for the athena-mind-adapter service, follow these steps:

    - **Edit the .env File**
    
        Open the .env file located in the root directory of the project. This file contains various environment variables that need to be set according to your specific configuration requirements. 

        Most environment variables in the .env file are predefined with default values. However, some values may need adjustment based on your specific setup. For instance, the MQ_CLIENT_HOST might need to be updated to match your Kafka server's address.
    
    - **Configuration Details**

        The .env file requires configuration for the following components:

        - **Logging**: Define the logging level and timezone.
        
        - **Message Queue (MQ)**: Configure settings for Kafka, including the host, consumer group ID, and topics.
        
        - **Tracing & Metrics (Optional)**: Configure enabling for opentelemetry, including the host.

        - **Adapter configuration**: Set the path to adapter JSON configuration file.


2. **Running the Application**
    - Run with Makefile: Follow this [instruction](#run-project-locally-installation-required)
    
    - Run with Docker Compose: 
        1. Open the Terminal 
        2. Navigate to the Root Directory
        3. Run Docker Compose
            ```
            docker compose up --build -d
            ```

## Connecting NLU to your adapters

To create remote connection to adapter for routing, follow these steps:

1. Add your new adapter configuration in [data/config.json](data/config.json) or in your specified path.

    **Example**: Adding two adapters `web_account`, and `general_handler` adapters.

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

    These configurations will be described with the following details.

    * __adapter__ - must be the name of folder inside `data` folder.
    * __name__ - name of adapter
    * __role__ - short description about role of chatbot 
    * __type__ - there are two types: `rag` and `custom`
    * __host__ - adapter endpoint
    * __config__
        * dataset_path - path to refer your dataset
        * dataset_doc_id - document key name
        * mongo_db_name - name of db in mongo
        * mongo_collection_name - name of collection in mongo
        * opensearch_index - name of index in opensearch
        * prompt
            * dir - directory that store prompt
            * query_generate_prompt - file name of prompt for query generation
            * qa_prompt - file name of prompt for question and answer prompt
            * response_control_prompt - file name of prompt for response control

## Customize Adapter Selecter Prompt (Optional) 

To customize how adapter selecter choose the adapter to handle the user query.

1. Navigate to [src/router/adapter_selecter.py](src/router/adapter_selecter.py).
2. On function `create_supervisor`, update your prompt on variable `system_prompt`.

    **Example**:
    ```python
    answer_format = '{{\"next\": ANSWER}}'
    system_prompt = f'''You are a supervisor tasked with managing a conversation between the following workers:  
    {member_prompt}
    Given the following user request, respond with the worker to act next. Each worker will perform a task and respond with their results and status. Answer in the raw JSON format ({answer_format})'''
    ```

## Project Structure
```bash
athena-mind-nlu
├── data
├── deployments
├── lib
│   ├── mq_client
├── scripts
├── src
│   ├── client
│   ├── common
│   ├── language_models
│   ├── router
│   ├── tests
│   └── main.py
├── .env
├── .python-version
├── chainlit.md
├── docker-compose.yml
├── Dockerfile
├── makefile
├── requirement-dev.txt
└── requirement.txt
```

### Description

- **data**: Contains adapter configuration and data.
- **deployments**: Contains required service docker-compose files for development.
- **lib**: Internal Library directory.
    - **mq_client**: Message queue client library.
- **src**: Source code directory.
    - **client**: Contains the code to start the service.
    - **common**: Includes common components.
    - **language_models**: Implementations of LLM service.
    - **router**: Implementations of Routing service.
    - **tests**: Contains unit test files for testing the code.
- **main.py**: The main entry point to start the service.
- **.env**: Environment variables configuration file.
- **.python-version**: Specifies the Python version used for the project.
- **chainlit.md**: Custom UI text file
- **docker-compose.yml**: docker-compose file to deploy the application for development.
- **Dockerfile**: Docker configuration file for containerizing the application.
- **Makefile**: Encapsulated commands to run the service on the terminal.
- **requirements-dev.txt**: Dependencies required in the development environment (e.g., unit testing dependencies).
- **requirements.txt**: Project dependencies required for running the application.