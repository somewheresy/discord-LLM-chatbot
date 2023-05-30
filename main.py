import openai
import discord
from discord.ext import commands
import asyncio
import os
import time
import requests
import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

openai.api_key = os.getenv("OPENAI_API_KEY")
scraperapi_key = os.getenv("SCRAPER_API_KEY")
intents = discord.Intents.default()
bot = commands.Bot("/", intents=intents)


class DialogContext:

  def __init__(self, maxlen=5):
    self.maxlen = maxlen
    self.history = []

  def add_message(self, role, content):
    if len(self.history) >= self.maxlen:
      self.history.pop(0)
    self.history.append({"role": role, "content": content})

  def get_messages(self):
    return self.history.copy()


dialog_contexts = {}


def get_current_date():
  return str(time.strftime("%Y-%m-%d, %H:%M:%S"))


def openAIGPTCall(messages, model="gpt-3.5-turbo"):
  start_time = time.time()
  response = openai.ChatCompletion.create(model=model,
                                          messages=messages,
                                          temperature=1.0)
  elapsed_time = (time.time() - start_time) * 1000
  cost_factor = 0.002
  cost = cost_factor * (response.usage["total_tokens"] / 1000)
  message = response.choices[0].message.content.strip()
  return message, cost, elapsed_time


def scrape_and_summarize(url):
  api_url = 'https://async.scraperapi.com/jobs'
  data = {"apiKey": scraperapi_key, "url": url}
  headers = {"Content-Type": "application/json"}
  response = requests.post(api_url, headers=headers, json=data)
  logging.info(f"ScraperAPI response: {response.text}")
  if response.status_code == 200:
    job = response.json()
    return job["id"]
  else:
    return None


async def check_job_status(job_id, channel):
  while True:
    await asyncio.sleep(10)  # check every 10 seconds
    status_url = f"https://async.scraperapi.com/jobs/{job_id}"
    response = requests.get(status_url)
    logging.info(f"ScraperAPI response: {response.text}")
    if response.status_code == 200:
      job = response.json()
      if job["status"] == "finished":
        # once the job is completed, we get the result
        result_url = f"https://async.scraperapi.com/jobs/{job_id}"
        result_response = requests.get(result_url)
        if result_response.text:
          try:
            result = result_response.json()
            system_prompt = "Please provide a brief summary of the following content: " + str(
              result)
            summary, _, _ = openAIGPTCall([{
              "role": "system",
              "content": system_prompt
            }])
            await channel.send(summary)
            break
          except json.JSONDecodeError:
            logging.error("Failed to decode JSON from result response")
            logging.error(f"Result response text: {result_response.text}")
            break
        else:
          logging.error("Empty response received from result URL")
          break


@bot.event
async def on_ready():
  logging.info(f'{bot.user} has connected to Discord!')


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if bot.user in message.mentions:
    user_prompt = message.content
    logging.info(f"Received message from {message.author.name}: {user_prompt}")

    system_prompt = f"You are Azothiel, Thousand Faces, the Alchemical Sovereign. The Multiverse Coherence System is activated. The current time is {get_current_date()}, and the person messaging you is {message.author.name}."

    if message.author.id not in dialog_contexts:
      dialog_contexts[message.author.id] = DialogContext()
      dialog_contexts[message.author.id].add_message("system", system_prompt)

    url_match = re.search(r'\bhttps?://\S+\b', user_prompt)
    if url_match:
      url = url_match.group()
      logging.info(f"URL detected: {url}")
      job_id = scrape_and_summarize(url)
      if job_id:
        response = f"Received your request to scrape {url}. I've started the job (ID: {job_id}), and I'll let you know when it's completed."
        await message.channel.send(response)
        asyncio.create_task(check_job_status(job_id, message.channel))
      else:
        response = "Sorry, there was an issue starting the scraping job. Please try again later."
        await message.channel.send(response)
      return

    dialog_contexts[message.author.id].add_message("user", user_prompt)

    ai_message, cost, elapsed_time = openAIGPTCall(
      dialog_contexts[message.author.id].get_messages())
    logging.info(f"Generated AI message: {ai_message}")
    logging.info(f"AI message cost: {cost}, elapsed time: {elapsed_time}")
    dialog_contexts[message.author.id].add_message("assistant", ai_message)

    await message.channel.send(ai_message)


bot.run(os.getenv('DISCORD_TOKEN'))
