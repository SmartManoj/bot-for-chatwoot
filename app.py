from flask import Flask, request, render_template, url_for, send_file, send_from_directory
import os
import urllib
import json
import requests
import psycopg2


from collections import defaultdict

app = Flask(__name__, static_url_path="/", static_folder='templates')


chatwoot_url = ''
chatwoot_bot_token = ''
bot_id = '1'


def create_js(questions):
    questions_as_string = json.dumps(questions)
    with open(f'templates/a3.js', 'w', encoding='utf8') as f:
        print(f'questions={questions_as_string}', file=f)


with open(f'templates/a3.js', 'r', encoding='utf8') as f:
    _ = f.read()[10:]
    try:
        pass
        questions = json.loads(_)
    except Exception as e:
        print(e)
        d = int(str(e).split()[-1][:-1])
        print(_[d - 10:d + 10])
        print('-' * 5)
        print(_[d - 100:d + 100])
# from a3 import questions
# def refresh_questions():
# 	global all_questions,questions
# 	with create_conn() as conn:
# 		with conn.cursor() as cur:
# 			cur.execute('select bot_id::text,json from bot')
# 			all_questions = dict(cur.fetchall())
# 			questions = all_questions[bot_id]
# 			create_js(questions)
from time import *
from datetime import *
from collections import *
data = defaultdict(dict)
uids = defaultdict(dict)
uid = '1'


def make_bot(bot_id):
    data[bot_id] = defaultdict(dict)


make_bot(bot_id)


import uuid


@app.route('/')
def index():
    return render_template('index.html')


# refresh_questions()
@app.route('/refresh')
def refresh():
    refresh_questions()
    return 'Done'


from threading import Thread

import traceback
from werkzeug.utils import secure_filename

l = 0


import pycronofy
import io


@app.route('/configure')
@app.route('/configure/<bot_id>')
def configure(bot_id='1'):
    start = 'start'
    v = {start}
    out = [(start, 0)]

    def tree(c):
        global l
        # answers=all_questions[bot_id][c]['answers']
        answers = questions[c]['answers']
        for i in answers:
            n = (i['nextId'])
            l += 1
            if (n != c) and n != '' and n not in v:
                out.append((n, l))
                v.add(n)
                if n in questions:
                    tree(n)
            else:
                break
        l = 0

    tree(start)
    print(out)
    for i in questions:
        if i not in v and '' != i:
            out.append((i, 0))
    return render_template('configure.html', random=uuid.uuid1(), triggers=out)


@app.route('/save/<bot_id>', methods=['post'])
def save(bot_id='1'):
    global questions
    if bot_id.isdigit():
        with create_conn() as conn:
            with conn.cursor() as cur:
                questions = request.json
                all_questions[bot_id] = questions
                questions = all_questions[bot_id]
                create_js(questions)
                v = json.dumps(questions).replace("'", "''")
                cur.execute(
                    f"update bot set json = ('{v}') where bot_id='{bot_id}' ")
            conn.commit()
        return 'done'
    else:
        return 'invalid bot_id', 400


import json
from collections import defaultdict

import requests


def chat(msg1, last_trigger, uid, bot_id):
    # questions = all_questions[bot_id]
    file_name = None
    name = data[bot_id][uid].get('name', uid)
    msg = msg1.lower()
    info = {}
    if msg == 'demo':
        trigger_name = msg
    elif msg.startswith('z'):
        trigger_name = msg
    elif last_trigger and msg not in ['start', 'hi']:
        lt = questions[last_trigger]
        if msg.isdigit() and (options := lt.get('input')):
            option_index = int(msg) - 1
            if 0 <= option_index < len(options):
                msg = options[option_index].lower()
            else:
                return 'Invalid Option', last_trigger, info
        for i in lt['answers']:
            ans = i.get('answer')
            if ans:
                if ans.lower() == msg:
                    trigger_name = i['nextId']
                    break
            else:
                trigger_name = i['nextId'] or 'start'
                break

    else:
        trigger_name = 'start'
    # print(questions)
    no_api = 1
    if trigger_name.startswith('api'):
        no_api = 0
        _, t, pn = trigger_name.split('_')
        text = 'from_api'
        trigger_name = 'start'
    if no_api:
        t = questions[trigger_name]
        text = t['botPrompt']

        if (options := t.get('input')):
            text += '\n' * 2 + \
                '\n'.join(f'{x+1}. {i}' for x, i in enumerate(options))
    return text, trigger_name, info


def send_to_chatwoot(account, conversation, message, info=None):
    if file_url := info.get('file_url'):
        data = {
            # 'content': message,
            'MediaUrl0': file_url,
            'MediaContentType0': 'application/pdf',
        }
    else:
        data = {
            'content': message
        }
    url = f"{chatwoot_url}/api/v1/accounts/{account}/conversations/{conversation}/messages"
    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "api_access_token": f"{chatwoot_bot_token}"}

    r = requests.post(url, json=data, headers=headers, timeout=1)
    # r = requests.post(url, files=formData, headers=headers)
    try:
        return r.json()
    except Exception as e:
        print(r.text)
        print(e)
        return r.text


@app.route('/rasa', methods=['POST'])
@app.route('/rasa/<bot_id>', methods=['POST'])
def rasa(bot_id='1'):
    data = request.get_json()
    message_type = data['message_type']
    message = data['content']
    conversation = data['conversation']['id']
    contact = data['sender']['id']
    account = data['account']['id']

    if(message_type == "incoming"):
        trigger_name = uids[bot_id].get(contact, '')
        bot_response, trigger_name, info = chat(
            message, trigger_name, contact, bot_id)
        uids[bot_id][contact] = trigger_name

        print(account, conversation, bot_response, info)
        create_message = send_to_chatwoot(
            account, conversation, bot_response, info)
        print(create_message)
        return create_message
    return message_type


if __name__ == "__main__":
    # app.run(debug=1)
    pass
else:
    alert()

if __name__ == '__main__':
    # app.run(debug=1)
    if 0:
        from livereload import Server
        app.debug = 1
        server = Server(app.wsgi_app)
        server.serve()
    l = ['start', '2', '1', '1', '2', '3']
    le = len(l)
    lee = 0
    while True:

        if lee < le:
            i = l.pop(0)
        else:
            i = input('>')
        lee += 1
        last_trigger = uids[bot_id].get(uid)
        a, trigger, info = chat(i, last_trigger, uid, bot_id)
        if trigger != 'end':
            uids[bot_id][uid] = trigger
            data[bot_id][uid]['last_msg'] = i
        print('>', i)
        print(a)
        if info:
            print(info)
        print('-' * 20)
