#!/usr/bin/env python
# coding: utf-8

# In[1]:


from typing import Literal
import json
import os
from datetime import datetime
import importlib
from itertools import chain
import pandas as pd
from tqdm import tqdm
from langchain import hub
from langchain_openai import ChatOpenAI


def load_module_from_path(path, module_name):
    """Загрузка модуля по указанному пути"""
    loader = importlib.machinery.SourceFileLoader(module_name, path)
    spec = importlib.util.spec_from_file_location(module_name, path, loader=loader)
    res_module = importlib.util.module_from_spec(spec)
    loader.exec_module(res_module)
    return res_module


def evaluate_news_article(text, config: dict[str, str | bool | int] = {}):
    """Оценка статьи"""
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    prompt = hub.pull(config.get("ai_parse_prompt", "mlenparrot/nlmk_aiparse"))
    params = {"text": text}
    chain = prompt | llm
    result = chain.invoke(params)
    return result


def run(config: dict[str, str | bool | int]):
    module = (
        load_module_from_path(config["gsheet_handler_lib_path"], "gsheet_handler")
        if "gsheet_handler_lib_path" in config
        else importlib.import_module("gsheet_handler")
    )
    importlib.reload(module)
    ggl = module.GSheetHandler("google_sheet_key.json")

    # Установка переменных окружения
    os.environ["LANGCHAIN_API_KEY"] = config["LANGCHAIN_API_KEY"]
    os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
    os.environ["LANGCHAIN_TRACING_V2"] = config.get("LANGCHAIN_TRACING_V2", "true")
    os.environ["LANGCHAIN_ENDPOINT"] = config.get(
        "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
    )
    os.environ["LANGCHAIN_PROJECT"] = config.get("LANGCHAIN_PROJECT", "nlmk_bot")

    parse_raw = ggl.extract_data_from_google_sheet(
        config.get(
            "PARSING_SITES_TABLE_URL",
            "https://docs.google.com/spreadsheets/d/1BA1nioQqc048FFvKXcpP5VqL_73kXNCcSx0m-jhI2MQ/edit?gid=1997913753#gid=1997913753",
        ),
        2,
    )[["url", "content"]][:3]

    def flatten_list(nested_list):
        return list(chain(*nested_list))

    parse_raw["combined_text"] = parse_raw["content"] + " " + parse_raw["url"]
    results = []
    for combined_text in tqdm(parse_raw["combined_text"], desc="Processing articles"):
        evaluation_result = evaluate_news_article(combined_text).get("news_list", [])
        results.append(evaluation_result)

    news_df = pd.DataFrame(flatten_list(results))
    news_df

    ggl.update_gsheet_with_df(
        news_df,
        config.get(
            "PARSING_SITES_TABLE_URL",
            "https://docs.google.com/spreadsheets/d/1BA1nioQqc048FFvKXcpP5VqL_73kXNCcSx0m-jhI2MQ/edit#gid=0",
        ),
        3,
    )  #  integer_columns=[3],
    #  float_columns=[4,5])

    news_df

    rss_raw = ggl.extract_data_from_google_sheet(
        config.get(
            "PARSING_SITES_TABLE_URL",
            "https://docs.google.com/spreadsheets/d/1BA1nioQqc048FFvKXcpP5VqL_73kXNCcSx0m-jhI2MQ/edit#gid=2038294867",
        ),
        1,
    )[["title", "link", "source", "content", "formatted_dates"]]
    rss_raw

    rss = rss_raw.copy()
    rss["content"] = rss["content"] + " источник: " + rss["source"]
    rss = rss.drop("source", axis=1)
    rss

    # Предположим, что ваши датафреймы уже загружены как news_df и rss

    # Переименуем столбцы в rss
    rss_renamed = rss.rename(
        columns={
            "title": "news_topic",
            "link": "link",
            "content": "news_text",
            "formatted_dates": "news_date",
        }
    )

    # Объединим два датафрейма
    combined_df = pd.concat([news_df, rss_renamed], ignore_index=True)

    # Получаем сегодняшнюю дату
    today = datetime.now().date()

    # Фильтруем по сегодняшней дате
    combined_df["news_date"] = pd.to_datetime(
        combined_df["news_date"], format="%Y-%m-%d", errors="coerce"
    )
    filtered_df = combined_df[combined_df["news_date"].dt.date == today].reset_index(
        drop=True
    )
    filtered_df

    ggl.update_gsheet_with_df(
        filtered_df,
        config.get(
            "PARSING_SITES_TABLE_URL",
            "https://docs.google.com/spreadsheets/d/1BA1nioQqc048FFvKXcpP5VqL_73kXNCcSx0m-jhI2MQ/edit#gid=0",
        ),
        4,
    )


def main():
    # Загрузка конфигурации из JSON-файла
    with open("config.json", encoding="utf-8") as config_file:
        config = json.load(config_file)
    run(config)


if __name__ == "__main__":
    main()
