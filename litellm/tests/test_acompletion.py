import pytest
from litellm import acompletion
from litellm import completion


def test_acompletion_params():
    import inspect
    from litellm.types.completion import CompletionRequest

    acompletion_params_odict = inspect.signature(acompletion).parameters
    completion_params_dict = inspect.signature(completion).parameters

    acompletion_params = {
        name: param.annotation for name, param in acompletion_params_odict.items()
    }
    completion_params = {
        name: param.annotation for name, param in completion_params_dict.items()
    }

    keys_acompletion = set(acompletion_params.keys())
    keys_completion = set(completion_params.keys())

    print(keys_acompletion)
    print("\n\n\n")
    print(keys_completion)

    print("diff=", keys_completion - keys_acompletion)

    # Assert that the parameters are the same
    if keys_acompletion != keys_completion:
        pytest.fail(
            "The parameters of the litellm.acompletion function and litellm.completion are not the same."
        )


@pytest.mark.asyncio
async def test_mock_acompletion():
    mock_response = "Hello there! How can I assist you today?"
    response = await acompletion(
        model="gpt-3.5-turbo",
        messages=[{"content": "Hello World", "role": "user"}],
        mock_response=mock_response
    )
    text_response = response["choices"][0]["message"]["content"]
    assert text_response == mock_response
