#### What this does ####
#    On success, logs events to Langsmith
from typing import Any, Callable

import dotenv, os
import requests
import requests
from datetime import datetime

dotenv.load_dotenv()  # Loading env variables using dotenv
import traceback
import asyncio
import types
from pydantic import BaseModel


def is_serializable(value: Any) -> bool:
    non_serializable_types = (
        types.CoroutineType,
        types.FunctionType,
        types.GeneratorType,
        BaseModel,
    )
    return not isinstance(value, non_serializable_types)


class LangsmithLogger:
    # Class variables or attributes
    def __init__(self) -> None:
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "litellm-completion")
        self.langsmith_default_run_name = os.getenv(
            "LANGSMITH_DEFAULT_RUN_NAME", "LLMRun"
        )

    def log_event(
        self,
        kwargs: dict[str, Any],
        response_obj: dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        print_verbose: Callable[[str, *Any], None],
    ) -> None:
        # Method definition
        # inspired by Langsmith http api here: https://github.com/langchain-ai/langsmith-cookbook/blob/main/tracing-examples/rest/rest.ipynb
        metadata = (
            kwargs.get("litellm_params", {}).get("metadata", {}) or {}
        )  # if metadata is None

        # set project name and run_name for langsmith logging
        # users can pass project_name and run name to litellm.completion()
        # Example: litellm.completion(model, messages, metadata={"project_name": "my-litellm-project", "run_name": "my-langsmith-run"})
        # if not set litellm will fallback to the environment variable LANGSMITH_PROJECT, then to the default project_name = litellm-completion, run_name = LLMRun
        project_name = metadata.get("project_name", self.langsmith_project)
        run_name = metadata.get("run_name", self.langsmith_default_run_name)
        print_verbose(
            f"Langsmith Logging - project_name: {project_name}, run_name {run_name}"
        )
        try:
            print_verbose(
                f"Langsmith Logging - Enters logging function for model {kwargs}"
            )
            import requests
            import datetime
            from datetime import timezone

            try:
                start_time: str = (
                    kwargs["start_time"].astimezone(timezone.utc).isoformat()
                )
                end_time: str = kwargs["end_time"].astimezone(timezone.utc).isoformat()
            except:
                start_time: str = datetime.datetime.utcnow().isoformat()
                end_time: str = datetime.datetime.utcnow().isoformat()

            # filter out kwargs to not include any dicts, langsmith throws an erros when trying to log kwargs
            new_kwargs = {}
            for key in kwargs:
                value = kwargs[key]
                if key == "start_time" or key == "end_time" or value is None:
                    pass
                elif type(value) == datetime.datetime:
                    new_kwargs[key] = value.isoformat()
                elif type(value) != dict and is_serializable(value=value):
                    new_kwargs[key] = value

            if isinstance(response_obj, BaseModel):
                try:
                    response_obj = response_obj.model_dump()
                except:
                    response_obj = response_obj.dict()

            print(f"response_obj: {response_obj}")

            data = {
                "name": run_name,
                "run_type": "llm",  # this should always be llm, since litellm always logs llm calls. Langsmith allow us to log "chain"
                "inputs": new_kwargs,
                "outputs": response_obj,
                "session_name": project_name,
                "start_time": start_time,
                "end_time": end_time,
            }
            print(f"data: {data}")

            response = requests.post(
                "https://api.smith.langchain.com/runs",
                json=data,
                headers={"x-api-key": self.langsmith_api_key},
            )

            if response.status_code >= 300:
                print_verbose(f"Error: {response.status_code}")
            else:
                print_verbose("Run successfully created")
            print_verbose(
                f"Langsmith Layer Logging - final response object: {response_obj}"
            )
        except:
            # traceback.print_exc()
            print_verbose(f"Langsmith Layer Error - {traceback.format_exc()}")
            pass
