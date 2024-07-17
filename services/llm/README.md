# athena-mind-llm

The athena-mind-llm project is designed to provide a robust and efficient service for leveraging Large Language Models (LLMs) in various applications.

## Overview

### Objective
   The primary objective of the athena-mind-llm project is to deliver high-performance language model services capable of handling diverse natural language processing tasks.

### Key Features
- **Flexibility**: Supports multiple LLMs such as HuggingFace and Gemini, allowing for easy switching and configuration based on specific requirements.
- **Ease of Deployment**: Integrates with DevOps API for streamlined deployment processes using Makefile and Docker Compose.
- **Custom Configuration**: Provides extensive configuration options for logging, message queue (MQ), and model-specific parameters.
- **Error Handling**: Robust error handling mechanisms with designated error queues to manage and resolve issues effectively.
- **Batch Processing**: Capable of batch processing requests to optimize resource usage and improve throughput.

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
    Also ensure that you have aligned the Kafka server address and the necessary configuration details in the .env file to connect to the Kafka cluster..

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
6. Create All Required Messaging Queue Topics
    ```
    make dkafka-create-all-topics
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
5. Send Sample Payload to LLM (TOPIC: Consuming Topic | MQ_PAYLOAD: Payload File in example/mq)
    ```
    make dkafka-publish-queue-json TOPIC="llm-request" MQ_PAYLOAD="llm"
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

    To configure the environment for the athena-mind-llm service, follow these steps:

    - **Edit the .env File**
    
        Open the .env file located in the root directory of the project. This file contains various environment variables that need to be set according to your specific configuration requirements. 

        Most environment variables in the .env file are predefined with default values. However, some values may need adjustment based on your specific setup. For instance, the KAFKA_HOST might need to be updated to match your Kafka server's address.
    
    - **Configuration Details**

        The .env file requires configuration for the following components:

        - **Logging**: Define the logging level and timezone.
        
        - **Message Queue (MQ)**: Configure settings for Kafka, including the host, consumer group ID, and topics.
        
        - **Service**: Set the service-specific variables.
        
        - **LLM Module**: Choose between HuggingFace or Gemini (key: `LLM_MODULE`) and configure the relevant settings based on your choice. After selecting the LLM module, configure only the necessary variables for the chosen module.


2. **Running the Application**
    - Run with Makefile: Follow this [instruction](#run-project-locally-installation-required)
    
    - Run with Docker Compose: 
        1. Open the Terminal 
        2. Navigate to the Root Directory
        3. Run Docker Compose
            ```
            docker compose up --build -d
            ```

## Model Update (for Hugging Face)

### Changing the Model 
To change the model, you can modify the `HUGGINGFACE_API_KEY` and `HUGGINGFACE_MODEL_PATH` variable in the [.env](.env) file. It can accept a path from either Hugging Face directly or a local model that you load. 

### Changing instruction tag
When changing the model, ensure that the tags wrapping the prompt at `START_PROMPT_TAG` and `END_PROMPT_TAG` in [src/internal/infra/ml/huggingface.py](src/internal/infra/ml/huggingface.py) are compatible with the new model. If the new model uses different tags, update these accordingly.

### Customize prompt
After using a model from Hugging Face, you should modify your prompt. Please follow the instructions to
* [Adapter Selector prompt](../../services/nlu/README.md#customize-adapter-selecter-prompt-optional).
* [RAG prompt](../../services/adapter/README.md#creating-an-adapter-using-predefined-rag).
  
### Modifying the Model Logic
If you need to change the logic of the model, you can edit the following files:

- [src/internal/infra/ml/huggingface.py](src/internal/infra/ml/huggingface.py) for **the model call and data transformation**

### Using GPU
We recommend you to use GPU instance to accelerate your LLM performance by adding this in docker-compose file at llm-service

```yaml
  services:
    service-llm:
      ## add this part under services.service-llm
      deploy:
        resources:
          reservations:
            devices:
              - driver: nvidia
                count: 1
                capabilities: [gpu]
```

 

## Project Structure
```bash
athena-mind-llm
├── doc
├── example
├── resources
├── src
│   ├── client
│   ├── internal
│   │   ├── app
│   │   │   ├── data_mapper
│   │   │   ├── external_service
│   │   │   └── service
│   │   ├── domain
│   │   │   ├── entity
│   │   │   ├── ml
│   │   │   └── service
│   │   ├── http
│   │   └── infra
│   │       ├── external_service
│   │       └── ml
│   ├── tests
│   └── main.py
├── .env
├── .python-version
├── Dockerfile
├── makefile
├── requirement-dev.txt
└── requirement.txt
```

### Description

- **doc**: Contains documentation related to the project.
- **example**: Includes examples to run the service with payload examples via MQ.
- **resources**: Directory for storing models used by the service.
- **src**: Source code directory.
- **client**: Contains the code to start the service.
- **common**: Includes common components used across different layers in the DDD architecture.
- **internal**: The core of the code following the Domain-Driven Design (DDD) architecture.
    - **app**: Application layer responsible for orchestrating application logic.
        - **data_mapper**: Handles transformation between Data Transfer Objects (DTO) and entities.
        - **external_service**: Interfaces for external services.
        - **service**: Contains application service interfaces and their implementations.
    - **domain**: Domain layer encapsulating business logic.
        - **entity**: Domain entities representing core business objects.
        - **ml**: Interfaces for machine learning models.
        - **service**: Contains domain service interfaces and their implementations.
    - **http**: Presentation layer, not used in this case.
    - **infra**: Infrastructure layer providing technical capabilities.
        - **external_service**: Implementations of external service interfaces.
        - **ml**: Implementations of machine learning models.
- **tests**: Contains unit test files for testing the code.
- **main.py**: The main entry point to start the service.
- **.env**: Environment variables configuration file.
- **.python-version**: Specifies the Python version used for the project.
- **Dockerfile**: Docker configuration file for containerizing the application.
- **Makefile**: Encapsulated commands to run the service on the terminal.
- **requirements-dev.txt**: Dependencies required in the development environment (e.g., unit testing dependencies).
- **requirements.txt**: Project dependencies required for running the application.