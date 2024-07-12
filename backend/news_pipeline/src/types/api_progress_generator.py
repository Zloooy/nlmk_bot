from typing import AsyncGenerator
from .api_progress import ApiProgress

type ApiProgressGenerator = AsyncGenerator[ApiProgress, None]