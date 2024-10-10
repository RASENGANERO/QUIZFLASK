from __future__ import unicode_literals
from flask import Flask, render_template, request, jsonify
import json
import alice_phrases
import logging
import threading
from random import choice
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG, filename='skill_logs.log', filemode='w')
# logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

WAIT = 0
REPLY = 1
STOP = 2

quest_data = json.load(open('quest_data.json'))

# Задаем параметры приложения Flask


@app.route("/skill", methods=['POST'])
def format_new_question(quest):
    question = choice(alice_phrases.questions)
    return question.format(quest=quest)


def timer_out(response, user_storage):
    user_storage['try'] += 1
    time_up = choice(alice_phrases.answer_time_up)
    right_answer = choice(alice_phrases.right_answer)
    real_answer = quest_data[user_storage['answer']]
    again = choice(alice_phrases.again)
    response.set_text('{time_up}\n{right_answer}{real_answer}\n{again}'.format(
        time_up=time_up,
        right_answer=right_answer,
        real_answer=real_answer,
        again=again
    ))
    buttons = [{
        "title": "Да",
        "hide": True
    }, {
        "title": "Нет",
        "hide": True
    }]
    response.set_buttons(buttons)
    # Выводим кнопочки
    user_storage['state'] = REPLY
    # Меняем состояние пользователя
    return response, user_storage


def handle_dialog(request, response, user_storage):
    if request.is_new_session:
        # Это новый пользователь. Инициализируем сессию и поприветствуем его.
        greetings = choice(alice_phrases.greetings)
        quest = ''
        user_storage = {
            'quest': quest,
            'state': STOP,
            # STOP-вопрос не задан, Wait-ожидается ответ, Reply - ответ получен
            'wins': 0,
            'tries': 0
        }
        response.set_text('{greetings}'.format(
            greetings=greetings
        ))

    if user_storage.get('state') == STOP:
        new_quest = choice(alice_phrases.new_quest)
        response.set_text('{new_quest}'.format(
            new_quest=new_quest
                ))
        buttons = [{
            "title": "Да",
            "hide": True
        }, {
            "title": "Нет",
            "hide": True
        }]
        response.set_buttons(buttons)
        if request.command.lower() == 'да':
            quest = choice(list(quest_data.keys()))
            user_storage = {
                'quest': quest,
                'state': WAIT,
                'wins': user_storage['wins'],
                'tries': user_storage['tries']
            }
            response.set_text(format_new_question(quest))
        elif request.command.lower() == 'нет':
            response.set_text("Хотите выйти?")
            buttons = [{
                "title": "Да",
                "hide": True
            }, {
                "title": "Нет",
                "hide": True
            }]
            response.set_buttons(buttons)
            if request.command.lower() == 'нет':
                user_storage['state'] = STOP
            elif request.command.lower() == 'да':
                response.set_end_session(True)
                goodbye = choice(alice_phrases.goodbye)
                response.set_text(goodbye)
            else:
                response.set_buttons(buttons)
                response.set_text('Извините, я не понимаю, вы хотите выйти?')
        else:
            buttons = [{
                "title": "Да",
                "hide": True
            }, {
                "title": "Нет",
                "hide": True
            }]
            response.set_buttons(buttons)
            response.set_text('Выберите один из двух вариантов - Да или Нет')
    if user_storage.get('state') == WAIT:
        # Обрабатываем ответ пользователя
        timer = threading.Timer(30.0, timer_out)
        timer.start()
        if request.command.lower() == quest_data[user_storage['answer']].lower():
            # Пользователь угадал
            user_storage['wins'] += 1
            user_storage['try'] += 1
            # Добавляем победу и попытку
            correct = choice(alice_phrases.answer_correct)
            again = choice(alice_phrases.again)
            # Выбираем реплику для поздравления

            response.set_text('{correct}\n{again}'.format(
                correct=correct,
                again=again
            ))
            # Поздравляем и спрашиваем, хочет ли пользователь сыграть ещё раз

            buttons = [{
                "title": "Да",
                "hide": True
            }, {
                "title": "Нет",
                "hide": True
            }]
            response.set_buttons(buttons)
            # Выводим кнопочки
            user_storage['state'] = REPLY
            # Меняем состояние пользователя
        else:
            user_storage['try'] += 1
            incorrect = choice(alice_phrases.answer_incorrect)
            right_answer = choice(alice_phrases.right_answer)
            real_answer = quest_data[user_storage['answer']]
            again = choice(alice_phrases.again)
            response.set_text('{incorrect}\n{right_answer}{real_answer}\n{again}'.format(
                incorrect=incorrect,
                right_answer=right_answer,
                real_answer=real_answer,
                again=again
            ))
            buttons = [{
                "title": "Да",
                "hide": True
            }, {
                "title": "Нет",
                "hide": True
            }]
            response.set_buttons(buttons)
            # Выводим кнопочки
            user_storage['state'] = REPLY
            # Меняем состояние пользователя
    elif user_storage.get('state') == REPLY:
        if request.command.lower() == 'да':
            quest = choice(list(quest_data.keys()))
            user_storage = {
                'quest': quest,
                'state': WAIT,
                'wins': user_storage['wins'],
                'tries': user_storage['tries']
            }
            response.set_text(format_new_question(quest))
        elif request.command.lower() == 'нет':
            response.set_end_session(True)
            goodbye = choice(alice_phrases.goodbye)
            response.set_text(goodbye)
        else:
            buttons = [{
                "title": "Да",
                "hide": True
            }, {
                "title": "Нет",
                "hide": True
            }]
            response.set_buttons(buttons)
            response.set_text('Выберите один из двух вариантов - Да или Нет')
    return response, user_storage


@app.route("/skill", methods=['GET'])
def main_get():
    return 'PLEASE POST'



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=False)
