import asyncio
import threading

import pytest

from language_models.mq_llm import MQLanguageModel


@pytest.mark.mq_llm
def test_start_thread():
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()


@pytest.mark.mq_llm
def test__call(mock_mq_client):
    llm = MQLanguageModel(mq=mock_mq_client)
    
    prompt = "You are a helpful assistant. Answer all questions to the best of your ability.\\nHuman: สวัสดี"
    
    loop = asyncio.get_event_loop()
    mock_mq_client.event_loop = loop
    mock_mq_client.send_request.return_value = {"results": "สวัสดีค่ะ ฉันชื่อจินตนา ฉันเป็นผู้ช่วยดิจิทัล มีอะไรที่ฉันช่วยได้ไหม"}
    results = llm._call(prompt=prompt)

    assert isinstance(results, str)
    assert results == "สวัสดีค่ะ ฉันชื่อจินตนา ฉันเป็นผู้ช่วยดิจิทัล มีอะไรที่ฉันช่วยได้ไหม"

    mock_mq_client.send_request.assert_called_once_with(llm.topic, {"text": prompt}, llm.consume_topic)


@pytest.mark.mq_llm
def test__call_got_none_result(mock_mq_client):
    loop = asyncio.get_event_loop()
    mock_mq_client.event_loop = loop
    mock_mq_client.send_request.return_value = {"results": None}

    prompt = "You are a helpful assistant. Answer all questions to the best of your ability.\\nHuman: สวัสดี"

    # case default fallback message
    llm = MQLanguageModel(mq=mock_mq_client)
    results = llm._call(prompt=prompt)

    assert isinstance(results, str)
    assert results == """ขออภัย, ฉันไม่พบข้อมูลที่ต้องการ กรุณาลองให้ข้อมูลเพิ่มเติมหรือถามคำถามใหม่ ฉันยินดีที่จะช่วยเหลือคุณเสมอ"""

    # case pass custom fallback message
    llm = MQLanguageModel(mq=mock_mq_client, fallback_message="test fallback")
    results = llm._call(prompt=prompt)

    assert isinstance(results, str)
    assert results == "test fallback"

@pytest.mark.asyncio
@pytest.mark.mq_llm
async def test__acall(mock_mq_client):
    llm = MQLanguageModel(mq=mock_mq_client)
    
    prompt = "You are a helpful assistant. Answer all questions to the best of your ability.\\nHuman: สวัสดี"
    
    mock_mq_client.send_request.return_value = {"results": "สวัสดีค่ะ ฉันชื่อจินตนา ฉันเป็นผู้ช่วยดิจิทัล มีอะไรที่ฉันช่วยได้ไหม"}
    results = await llm._acall(prompt=prompt)

    assert isinstance(results, str)
    assert results == "สวัสดีค่ะ ฉันชื่อจินตนา ฉันเป็นผู้ช่วยดิจิทัล มีอะไรที่ฉันช่วยได้ไหม"

    mock_mq_client.send_request.assert_called_once_with(llm.topic, {"text": prompt}, llm.consume_topic)

@pytest.mark.asyncio
@pytest.mark.mq_llm
async def test__acall_got_none_result(mock_mq_client):
    loop = asyncio.get_event_loop()
    mock_mq_client.event_loop = loop
    mock_mq_client.send_request.return_value = {"results": None}

    prompt = "You are a helpful assistant. Answer all questions to the best of your ability.\\nHuman: สวัสดี"

    # case default fallback message
    llm = MQLanguageModel(mq=mock_mq_client)
    results = await llm._acall(prompt=prompt)

    assert isinstance(results, str)
    assert results == """ขออภัย, ฉันไม่พบข้อมูลที่ต้องการ กรุณาลองให้ข้อมูลเพิ่มเติมหรือถามคำถามใหม่ ฉันยินดีที่จะช่วยเหลือคุณเสมอ"""

    # case pass custom fallback message
    llm = MQLanguageModel(mq=mock_mq_client, fallback_message="test fallback")
    results = await llm._acall(prompt=prompt)

    assert isinstance(results, str)
    assert results == "test fallback"
