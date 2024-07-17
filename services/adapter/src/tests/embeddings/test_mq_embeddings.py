import asyncio
import threading

import pytest

from embeddings.mq_embeddings import MQEmbeddings


@pytest.mark.mq_embeddings
def test_start_thread():
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()

@pytest.mark.mq_embeddings
def test_embed_documents(mock_mq_client):
    embeddings = MQEmbeddings(mq=mock_mq_client)
    
    texts = [
        "how much protein should a female eat",
    ]
    
    loop = asyncio.get_event_loop()
    mock_mq_client.event_loop = loop
    mock_mq_client.send_request.return_value = {"results": [[0.1, 0.2, 0.3]]}
    results = embeddings.embed_documents(texts=texts)

    assert len(results) == 1
    assert results == [[0.1, 0.2, 0.3]]

    mock_mq_client.send_request.assert_called_once_with(embeddings.topic, {"texts": texts}, embeddings.consume_topic)

@pytest.mark.mq_embeddings
def test_embed_query(mock_mq_client):
    embeddings = MQEmbeddings(mq=mock_mq_client)
    
    text = "how much protein should a female eat"
    
    loop = asyncio.get_event_loop()
    mock_mq_client.event_loop = loop
    mock_mq_client.send_request.return_value = {"results": [[0.1, 0.2, 0.3]]}
    result = embeddings.embed_query(text=text)

    assert result == [0.1, 0.2, 0.3]

    mock_mq_client.send_request.assert_called_once_with(embeddings.topic, {"texts": [text]}, embeddings.consume_topic)


@pytest.mark.asyncio
@pytest.mark.mq_embeddings
async def test_aembed_documents(mock_mq_client):
    embeddings = MQEmbeddings(mq=mock_mq_client)
    
    texts = [
        "how much protein should a female eat",
    ]
    
    mock_mq_client.send_request.return_value = {"results": [[0.1, 0.2, 0.3]]}
    results = await embeddings.aembed_documents(texts=texts)

    assert len(results) == 1
    assert results == [[0.1, 0.2, 0.3]]

    mock_mq_client.send_request.assert_called_once_with(embeddings.topic, {"texts": texts}, embeddings.consume_topic)


@pytest.mark.asyncio
@pytest.mark.mq_embeddings
async def test_aembed_query(mock_mq_client):
    embeddings = MQEmbeddings(mq=mock_mq_client)
    
    text = "how much protein should a female eat"
    
    loop = asyncio.get_event_loop()
    mock_mq_client.event_loop = loop
    mock_mq_client.send_request.return_value = {"results": [[0.1, 0.2, 0.3]]}
    result = await embeddings.aembed_query(text=text)

    assert result == [0.1, 0.2, 0.3]

    mock_mq_client.send_request.assert_called_once_with(embeddings.topic, {"texts": [text]}, embeddings.consume_topic)
