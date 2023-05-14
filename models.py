from dotenv import load_dotenv
import os
import openai
from time import time,sleep

# Initialist environment viables
load_dotenv()

# Import open AI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# system message chatbot is optional
systembot = open_file('systembot.txt')


# ChatGPT 3.5-turbo - default model
def chatgpt3(userinput, temperature=0.6, frequency_penalty=0, presence_penalty=0):
    max_retry = 6
    retry = 0
    messagein = [
        {"role": "user", "content": userinput },
        {"role": "system", "content": systembot}]
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=messagein
            )
            text = response['choices'][0]['message']['content']
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)          


# GPT 3 with text-davinci-003 API - slightly more expensive, possibly better results
def gpt_3(prompt, engine='text-davinci-003', temp=0.5, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


# ChatGPT4 is not default and is optional - most expensive
def chatgpt4(userinput, temperature=0.7, frequency_penalty=0, presence_penalty=0):
    max_retry = 6
    retry = 0
    messagein = [
        {"role": "user", "content": userinput },
        {"role": "system", "content": systembot}]
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=messagein
            )
            text = response['choices'][0]['message']['content']
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT4 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)          
