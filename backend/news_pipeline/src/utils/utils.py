import logging
from asyncio import Future, get_event_loop
from nbconvert.preprocessors import ExecutePreprocessor
from nbparameterise import replace_definitions, parameter_values, extract_parameters
from typing import Any
from nbformat import read as read_notebook, NotebookNode

logger = logging.getLogger()


def execute_notebook(notebook: NotebookNode) -> Future[None]:
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

    def nb_runner(nb: NotebookNode, metadata: dict[str, dict[str, str]]) -> None:
        ep.preprocess(nb, metadata)
        return None

    return get_event_loop().run_in_executor(
        None, nb_runner, notebook, {"metadata": {"path": "./"}}
    )


def load_notebook(
    notebook_path: str, config: dict[str, str | bool | int]
) -> NotebookNode:
    nb = None
    with open(notebook_path, encoding="utf-8") as f:
        nb = read_notebook(f, as_version=4)
    original_params = extract_parameters(nb)
    return replace_definitions(nb, parameter_values(original_params, config=config))
