
async def mock_async_generator(responses):
    for response in responses:
        yield response