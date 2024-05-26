# Задача

Разработать прототип, который будет автоматически собирать и анализировать информацию с выбранных сайтов, формировать дайджест новостей и выделять самую важную информацию для ИТ подразделения.

## Подробнее о кейсе НЛМК

ИТ подразделение сталелитейной компании нуждается в оперативной информации о новейших продуктах, инициативах конкурентов, инновациях в системах хранения и управления данными, законодательных требованиях, открытиях и других событиях, которые могут повлиять на стратегию компании. В настоящее время поиск информации происходит вручную, что требует больших временных затрат и может привести к упущению важных событий.

## План действий команды

### 1. Подготовительный этап

#### 1.1 Сбор требований
- Определить конкретные потребности ИТ подразделения НЛМК.
- Составить список ключевых тем: новейшие продукты, инициативы конкурентов, инновации в системах хранения и управления данными, законодательные требования, открытия и т.д.
- Уточнить требования к формату дайджеста и периодичности обновлений.

#### 1.2 Анализ источников
- Определить релевантные источники информации: новостные сайты, блоги, форумы, официальные сайты конкурентов и регуляторов.
- Составить список URL-адресов для мониторинга.

### 2. Архитектура системы

#### 2.1 Выбор технологий
- Язык программирования: Python.
- Библиотеки для веб-скрейпинга: Selenium.
- Система хранения данных: ChromaDB.
- Средства анализа данных: OpenAI API (GPT-4).
- Интерфейс для отображения результатов: Streamlit.

#### 2.2 Определение модулей системы
- Модуль сбора данных (веб-скрейпинг с использованием Selenium).
- Модуль хранения данных (ChromaDB).
- Модуль анализа данных с использованием OpenAI API.
- Модуль генерации дайджеста с помощью OpenAI API.
- Модуль отображения данных (Streamlit и Telegram Bot).

### 3. Разработка прототипа

## Архитектурная схема

```mermaid
flowchart TD
    User --> Interface
    Interface --> Scraper
    Scraper --> Storage
    Storage --> Retrieval
    Retrieval --> Analysis
    Analysis --> Digest
    Digest --> Interface
    Digest --> TelegramBot
    
    Analysis --> DisplayStreamlit
    Analysis --> DisplayTelegram
    
    User[User]
    Interface[Interface Streamlit]
    Scraper[Data Collection Selenium]
    Storage[Data Storage ChromaDB]
    Retrieval[Information Retrieval]
    Analysis[Data Analysis OpenAI API]
    Digest[Digest Generation OpenAI API]
    DisplayStreamlit[Display Results Streamlit]
    DisplayTelegram[Display Results Telegram Bot]
    TelegramBot[Telegram Bot]

```markdown

1. **User**: Пользователь взаимодействует с интерфейсом через Streamlit или Telegram Bot.
2. **Interface (Streamlit)**: Веб-интерфейс для отображения данных.
3. **Data Collection (Selenium)**: Модуль для сбора данных с выбранных веб-источников.
4. **Data Storage (ChromaDB)**: Система для хранения собранных данных.
5. **Information Retrieval**: Модуль для извлечения релевантной информации из хранилища данных.
6. **Data Analysis (OpenAI API)**: Анализ данных и генерация текста с помощью OpenAI API.
7. **Digest Generation (OpenAI API)**: Генерация дайджеста новостей на основе извлеченной и проанализированной информации.
8. **Display Results (Streamlit)**: Отображение результатов в веб-интерфейсе.
9. **Display Results (Telegram Bot)**: Отправка результатов через Telegram Bot.

