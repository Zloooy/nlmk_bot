from typing import Callable
from .api_progress_generator import ApiProgressGenerator

type ApiRunner = Callable[[], ApiProgressGenerator]