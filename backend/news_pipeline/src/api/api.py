"""Модуль для запуска web-сервера и маппинга бизнес-логики на REST-запросы"""

import asyncio
import logging
from aiohttp import web
import nest_asyncio
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings, SwaggerInfo
from models import Config
from .types.api_runner import ApiRunner

# Apply nest_asyncio to allow nested event loops in Jupyter Notebook
nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Словарь для хранения состояния выполнения для каждого этапа
progress = {
    "run_scrape": 0,
    "run_summarization": 0,
    "run_grade": 0,
    "run_digest_generation": 0,
}


async def get_progress(request):
    """
    ---
    description: Get the progress of a specific step
    tags:
    - Progress
    parameters:
    - name: token
      in: query
      required: true
      schema:
        type: string
    - name: step
      in: path
      required: true
      schema:
        type: string
    responses:
      '200':
        description: Progress status
      '400':
        description: Invalid step
      '403':
        description: Invalid token
    """
    token = request.query.get("token")
    if token != "your_secret_token":
        return web.json_response({"error": "Invalid token"}, status=403)

    step = request.match_info.get("step")
    if step not in progress:
        return web.json_response({"error": "Invalid step"}, status=400)

    return web.json_response({"step": step, "progress": progress[step]}, status=200)


def run(
    config: Config,
    run_scrape: ApiRunner,
    run_summarization: ApiRunner,
    run_grade: ApiRunner,
    run_digest_generation: ApiRunner,
):
    """Запуск web-сервера с параметрами из config и коллбеками для выполнения методов"""
    if None in (
        config,
        run_scrape,
        run_summarization,
        run_grade,
        run_digest_generation,
    ):
        raise ValueError("Some arguments are empty")
    security_token = config.get("token", "your_secret_token")

    def token_checker(request):
        token = request.query.get("token")
        if token != security_token:
            return web.json_response({"error": "Invalid token"}, status=403)
        return None

    async def progress_generator_wrapper(api_runner: ApiRunner, step: str):
        progress[step] = 0
        try:
            async for api_progress in api_runner():
                progress[step] = api_progress.progress
        except (TypeError, OSError) as e:
            logger.exception(e)
            progress[step] = -1
            return None
        progress[step] = 0

    def request_processor(
        request,
        api_runner: ApiRunner,
        step: str,
        status_message: str,
    ):
        result = token_checker(request)
        if result:
            return result
        asyncio.create_task(progress_generator_wrapper(api_runner, step))
        return web.json_response(
            {
                "status": status_message,
                "notebooks": [],
                "message": "",
            },
            status=200,
        )

    def scrape_endpoint(request):
        """
        ---
        description: Run the scrape notebooks
        tags:
        - Notebook Execution
        parameters:
        - name: token
          in: query
          required: true
          schema:
            type: string
        responses:
          '200':
            description: Scrape notebook execution started
          '400':
            description: Notebook not found
          '403':
            description: Invalid token
        """
        return request_processor(
            request, run_scrape, "run_scrape", "Scrape notebook execution started"
        )

    def summarization_endpoint(request):
        """
        ---
        description: Run the summarization notebook
        tags:
        - Notebook Execution
        parameters:
        - name: token
          in: query
          required: true
          schema:
            type: string
        responses:
          '200':
            description: Summarization notebook execution started
          '400':
            description: Notebook not found
          '403':
            description: Invalid token
        """
        return request_processor(
            request,
            run_summarization,
            "run_summarization",
            "Summarization notebook execution started",
        )

    def grade_endpoint(request):
        """
        ---
        description: Run the grade notebook
        tags:
        - Notebook Execution
        parameters:
        - name: token
          in: query
          required: true
          schema:
            type: string
        responses:
          '200':
            description: Grade notebook execution started
          '400':
            description: Notebook not found
          '403':
            description: Invalid token
        """
        return request_processor(
            request, run_grade, "run_grade", "Run the grade notebook"
        )

    def digest_generation_endpoint(request):
        """
        ---
        description: Run the digest generation notebook
        tags:
        - Notebook Execution
        parameters:
        - name: token
          in: query
          required: true
          schema:
            type: string
        responses:
          '200':
            description: Digest generation notebook execution started
          '400':
            description: Notebook not found
          '403':
            description: Invalid token
        """
        return request_processor(
            request,
            run_digest_generation,
            "run_digest_generation",
            "Run the digest generation notebook",
        )

    app = web.Application()

    # Swagger документация
    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path="/docs"),
        info=SwaggerInfo(
            title="Jupyter Notebook Runner API",
            version="1.0",
            description="An API to run Jupyter notebooks",
        ),
    )

    # Добавление маршрутов
    swagger.add_routes(
        [
            web.get("/run_scrape", scrape_endpoint),
            web.get("/run_summarization", summarization_endpoint),
            web.get("/run_grade", grade_endpoint),
            web.get("/run_digest_generation", digest_generation_endpoint),
            web.get("/progress/{step}", get_progress),
        ]
    )
    web.run_app(
        app,
        host=str(config.get("host", "0.0.0.0")),
        port=int(config.get("port", 35474)),
    )
