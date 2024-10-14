from flask import Flask, render_template, jsonify, session, request, g
import logging
import sqlite3


app = Flask(__name__)
app.secret_key = "43s0d448@$%6"
logging.basicConfig(level=logging.DEBUG, filename='skill_logs.log', filemode='w')

DATABASE = 'quizdb.db'

def getMaxParts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT MAX(quizpart_id) AS COUNT FROM quiz_parts;")
    data = cursor.fetchone()
    return int(data[0])

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

def get_data(number):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT qq.quest_id, qq.quest_name, qp.quizpart_name FROM quiz_questions AS qq INNER JOIN quiz_parts AS qp ON qq.quest_partid = qp.quizpart_id WHERE qp.quizpart_id=?", (number,))
    data = cursor.fetchall()
    return data

def checkDataAnswer(dt1,dt2):
    if str(dt1).strip().lower()==str(dt2).strip().lower():
        return 1
    return 0

def getDataAnswered():
    dataSess = session['dataAnswer']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT qq.quest_id, qp.quizpart_name, qp.quizpart_id, qq.quest_name, qq.quest_answer FROM quiz_questions AS qq INNER JOIN quiz_parts AS qp ON qq.quest_partid = qp.quizpart_id")
    data = cursor.fetchall()
    from pprint import pprint
    pprint(data)
    pprint(dataSess)
    dataFinal = []
    dtsq = {}
    balls=0
    for v in range(1,getMaxParts()+1):
        dataAnswers = dataSess["data"+str(v)]
        dataPart = [a for a in data if a[2]==int(v)]
         
        lk = []
        for pk in range(len(dataPart)):
            checkes=checkDataAnswer(dataAnswers[int(pk)],dataPart[pk][4])
            lk.append([
                dataPart[pk][0],
                dataPart[pk][3],
                dataAnswers[int(pk)],
                dataPart[pk][4],
                checkes
                ])
            balls+=checkes
        #print(lk)
        dtsq[dataPart[pk][1]]=lk
        #print(dtsq)
    return [dtsq,balls]


def getFormattedData(data):
    keys = list(data.keys())
    for v in range(len(keys)):
        if str(keys[v]).startswith("data")!=True:
            del data[keys[v]]
    return data

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/skillreport/", methods=['GET'])
def skillreport():
    data = getDataAnswered()
    return render_template('skillreport.html',data=data[0],balls=data[1])

@app.route("/skill/<int:number>/", methods=['GET'])
def getskill(number):
    data = get_data(number)
    return render_template('skill.html', data=data, name=data[0][2], number=number)


@app.route("/skillanswer/<int:number>/", methods=['POST'])
def skillanswer(number):
    data_all = request.get_json()  # Получаем данные в формате JSON
    data_json = [str(a).strip() for a in str(data_all['data']).split("\n")]

    if 'dataAnswer' not in session or session['dataAnswer'] is None:
        session['dataAnswer'] = {}
    
    dt = session['dataAnswer']
    
    dt["data"+str(number)] = data_json
    dt = getFormattedData(dt)
    
    session['dataAnswer'] = dt
    session.modified = True
    from pprint import pprint
    pprint(session['dataAnswer'])

    number = int(data_all['listid']) + 1
    response_data = {}
    
    if int(number) <= int(getMaxParts()):
        response_data = {"next": str(number), "isfinal": "false"}
    else:
        response_data = {"isfinal": "true"}

    return jsonify(response_data)


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)