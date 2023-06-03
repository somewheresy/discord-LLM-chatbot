# Discord OpenAI Chatbot

## Overview

This program creates a Discord chatbot using the OpenAI GPT-4 model. The chatbot supports text generation, URL scraping, text summarization, and web search functionalities. 

Features:

1. Converses with users in a Discord server using the OpenAI GPT-4 model.
2. Scrapes URLs provided by users, summarizes the content using the GPT-4 model.
3. Supports web search using the Brave Search API.

## Requirements

To run the bot, the following environment variables should be set:
1. `OPENAI_API_KEY`: Your OpenAI API key.
2. `SCRAPER_API_KEY`: Your Scraper API key.
3. `BRAVE_SEARCH_API_KEY`: Your Brave Search API key.
4. `DISCORD_TOKEN`: Your Discord bot token.

The bot requires the following Python packages:
- openai
- discord.py
- asyncio
- os
- time
- requests
- re
- json
- logging

Please install these dependencies using pip:

```shell
pip install openai discord.py asyncio requests regex json logging
```
Or alternatively use Poetry:

```shell
poetry install
```

## Usage

To start the bot, run the Python file.

```shell
python main.py
```

## Commands

1. To talk to the bot, mention the bot in your Discord message.
2. To set the model's temperature (for randomness in responses), include `::temperature=value::` in your message. For example: `::temperature=0.5::`.
3. To specify a model, include `::model=model_id::` in your message. For example: `::model=gpt-3.5-turbo::`.
4. To scrape and summarize a URL, simply include the URL in your message.
5. To perform a web search, include `::search your_search_query::` in your message. For example: `::search python tutorials::`.

## Note

This bot leverages both OpenAI and the Scraper API to provide text generation and website scraping services. Please be aware of any usage costs associated with these APIs. This bot also uses the Brave Search API for web search functionalities. As of the last update (June 2023), Brave Search API is free to use, but this may change in the future. Please consult the respective API documentation for the latest details.
