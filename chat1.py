#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import datetime
import openai

chat_log = None

load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')
completion = openai.Completion()

start_chat_log = '''...  '''

def ask(question, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    prompt = f'{chat_log}Human: {question}\nChatBot:'
    response = completion.create(
        prompt=prompt,
        engine="text-davinci-003",
        stop=['\nHuman'],
        temperature=0.9,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        best_of=1,
        max_tokens=1500)
    answer = response.choices[0].text.strip()
    return answer


def chat_interaction(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    return f'{chat_log}\n\n\nHuman: {question}\n\nChatBot: {answer}\n\n\n'


while True:
    question = input("Ask a question traveler: ")

    answer = ask(question, chat_log)
    chat_log = chat_interaction(question, answer, chat_log)
    time_stamp = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")
    chat_log_file = 'archive-messages/output_'+time_stamp+'.log'

    with open(chat_log_file, 'w') as outfile:
        outfile.write(chat_log)
    print(str(chat_log))

    if question == 'quit' or question == 'q':
        print(f"Bye, see ya later! ;)\n Remember.. our convo is saved in {chat_log_file} \nHasta la vista! Keep it wild and wacky!\n")
        break

