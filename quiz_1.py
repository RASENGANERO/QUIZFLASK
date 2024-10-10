from flask import Flask, render_template, request, jsonify
import json
import alice_phrases
import logging
import threading
from random import choice

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, filename='skill_logs.log', filemode='w')



WAIT = 0
REPLY = 1
STOP = 2

quest_data = json.load(open('quest_data.json'))

@app.route("/")
def index():
    data = [
        "Привет! Отправь мне свой ответ!",
        "Как твои дела?"
    ]
    return render_template('index.html',title=data[0],question=data[1])

@app.route("/skill", methods=['POST'])
def skill():
    user_input = request.form.get('command')
    user_id = request.remote_addr  # Use IP address as a simple session identifier

    if user_id not in sessionStorage:
        sessionStorage[user_id] = {
            'quest': '',
            'state': STOP,
            'wins': 0,
            'tries': 0
        }

    user_storage = sessionStorage[user_id]
    response = handle_dialog(user_input, user_storage)
    sessionStorage[user_id] = user_storage

    return jsonify({'text': response.get('text', 'Error occurred')})

def handle_dialog(user_input, user_storage):
    if user_storage['state'] == STOP:
        if user_input.lower() == 'да':
            quest = choice(list(quest_data.keys()))
            user_storage['quest'] = quest
            user_storage['state'] = WAIT
            return {"text": format_new_question(quest)}
        elif user_input.lower() == 'нет':
            return {"text": "Хотите выйти?"}
        else:
            return {"text": "Выберите один из двух вариантов - Да или Нет"}

    elif user_storage['state'] == WAIT:
        timer = threading.Timer(30.0, timer_out, [user_storage])
        timer.start()
        if user_input.lower() == quest_data[user_storage['quest']].lower():
            user_storage['wins'] += 1
            user_storage['state'] = REPLY
            return {"text": f"{choice(alice_phrases.answer_correct)}\nХотите сыграть еще раз?"}
        else:
            user_storage['state'] = REPLY
            return {"text": f"{choice(alice_phrases.answer_incorrect)}\n{choice(alice_phrases.right_answer)}: {quest_data[user_storage['quest']]}"}

    elif user_storage['state'] == REPLY:
        if user_input.lower() == 'да':
            quest = choice(list(quest_data.keys()))
            user_storage['quest'] = quest
            user_storage['state'] = WAIT
            return {"text": format_new_question(quest)}
        elif user_input.lower() == 'нет':
            user_storage['state'] = STOP
            return {"text": choice(alice_phrases.goodbye)}

    return {"text": "Произошла ошибка, попробуйте снова."}

def format_new_question(quest):
    question = choice(alice_phrases.questions)
    return question.format(quest=quest)

def timer_out(user_storage):
    user_storage['state'] = REPLY
    # Add logic for timeout handling if needed

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)

