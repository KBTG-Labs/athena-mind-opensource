import pytest

from internal.infra.ml import VectorModel


@pytest.mark.vector_model
def test_vector_model_process_one_batch_size(mock_vector_model):
    model = VectorModel(model_path="", model_batch_size=32,
                        model_max_characters=500)
    model.model = mock_vector_model
    texts = [
        "how much protein should a female eat",
    ]
    mock_vector_model.encode.return_value = [[0.1, 0.2, 0.3]]
    results = model.process(texts)
    assert len(results) == 1
    assert results == [[0.1, 0.2, 0.3]]
    mock_vector_model.encode.assert_called_once()


@pytest.mark.vector_model
def test_vector_model_process_multiple_batch_size(mock_vector_model):
    model = VectorModel(model_path="", model_batch_size=32,
                        model_max_characters=500)
    model.model = mock_vector_model

    total = model.model_batch_size * 4 + 5
    texts = [
        "how much protein should a female eat",
    ] * total

    mock_responses = [
        [[0.1, 0.2, 0.3]] * i
        for i in
        [model.model_batch_size] * (total // model.model_batch_size) +
        [total % model.model_batch_size]
    ]
    mock_vector_model.encode.side_effect = mock_responses
    results = model.process(texts)
    assert len(results) == total
    assert mock_vector_model.encode.call_count == 5
    mock_vector_model.encode.assert_any_call(texts[:model.model_batch_size])
    mock_vector_model.encode.assert_any_call(texts[:5])
