"""Модуль для связывания конфигурации, бизнес-логики и api в единое целое"""

import json
from typing import Collection
from os.path import join as path_join, abspath
from math import floor
from nbformat import NotebookNode
from api import ApiRunner, ApiProgressGenerator, ApiProgress, run as run_api
from utils import load_notebook, execute_notebook
from models import Config

SCRAPE_FOLDER = "scrape"
RANGE_SUMMARY_FOLDER = "range_summary"
DIGEST_GENERATION_FOLDER = "digest_generation"


async def execute_notebooks(
    notebooks: Collection[NotebookNode],
) -> ApiProgressGenerator:
    """Последовательный запуск ноутбуков с возвращением прогресса"""
    total = len(notebooks)
    yield ApiProgress(progress=0)
    for i, nb in enumerate(notebooks):
        await execute_notebook(nb)
        yield ApiProgress(progress=floor(total / (i + 1) * 100))


def run_scrape(config: Config) -> ApiRunner:
    """Запуск сбора исходных данных для дайджеста"""
    ai_scrape_nb = load_notebook(path_join(SCRAPE_FOLDER, "scrape.ipynb"), config)
    rss_nb = load_notebook(path_join(SCRAPE_FOLDER, "rss.ipynb"), config)
    news_extraction_nb = load_notebook(
        path_join(SCRAPE_FOLDER, "news_extraction.ipynb"), config
    )

    async def runner() -> ApiProgressGenerator:
        async for pr in execute_notebooks([ai_scrape_nb, rss_nb, news_extraction_nb]):
            yield pr

    return runner


def run_summarization(config: Config) -> ApiRunner:
    """Оценка и суммаризация текстов статей"""
    news_range_n_summary_nb = load_notebook(
        path_join(RANGE_SUMMARY_FOLDER, "news_range_n_summary.ipynb"), config
    )

    async def runner() -> ApiProgressGenerator:
        async for pr in execute_notebooks([news_range_n_summary_nb]):
            yield pr

    return runner


# Этапы оценки и суммаризации объединeны
run_grade = run_summarization


def run_digest_generation(config: Config) -> ApiRunner:
    """Заполнение шаблона дайджеста"""
    digest_generation_nb = load_notebook(
        path_join(DIGEST_GENERATION_FOLDER, "didgest.ipynb"), config
    )

    async def runner() -> ApiProgressGenerator:
        async for pr in execute_notebooks([digest_generation_nb]):
            yield pr

    return runner


def run() -> None:
    """Запуск проекта с внедрёнными зависимостями"""
    config: Config = {}
    file_path_config_keys = ["google_sheet_key_path", "gsheet_handler_lib_path"]
    # Загрузка конфигурации из JSON-файла
    with open("config.json", encoding="utf-8") as config_file:
        config = json.load(config_file)
    file_path_config_keys = ["google_sheet_key_path", "gsheet_handler_lib_path"]
    # Замена относительных путей на абсолютные для их использование в Notebook
    for key in file_path_config_keys:
        config[key] = abspath(config[key])
    # Инициализация конвейера новостей
    run_api(
        config=config,
        run_scrape=run_scrape(config),
        run_summarization=run_summarization(config),
        run_grade=run_grade(config),
        run_digest_generation=run_digest_generation(config),
    )
