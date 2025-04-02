from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_session import Session
import os
from random import sample, choices
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def generar_numero():
    numero_gen = sample(range(10), 4)
    return numero_gen

def generar_diccionario():
    diccionario = {}
    while len(diccionario) < 5000:
        numero = generar_numero()
        numero_str = ''.join(map(str, numero))
        if numero_str not in diccionario:
            diccionario[numero_str] = {
                'estado': choices([0, 1], weights=[0.7, 0.3], k=1)[0],
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'valor_premio': '$150.000.000'
            }
    print(f"Diccionario generado con {len(diccionario)} elementos")
    return diccionario

def escoger_numero(dic):
    winner_key = sample(list(dic.keys()), 1)[0]
    winner = (winner_key, dic[winner_key])
    print("Número Ganador: ", winner[0])
    return winner

def message_creation(winner):
    if winner[1]['estado'] == 0:
        message = f"El número {winner[0]} no fue comprado, por lo cual el premio no será repartido."
        print(message)
    else:
        message = f"El número {winner[0]} fue comprado, por lo cual el premio será repartido al ganador."
        print(message)
    return message

@app.route('/')
def index():
    if 'dictionaries' not in session or 'winners' not in session:
        session['dictionaries'] = {
            'dic1': generar_diccionario(),
            'dic2': generar_diccionario(),
            'dic3': generar_diccionario()
        }
        session['winners'] = {
            'dic1': None,
            'dic2': None,
            'dic3': None
        }
        session.modified = True  # Ensure the session is updated

    return render_template('index.html')

@app.route('/tickets/<int:dic_num>/<int:page>')
def tickets(dic_num, page):
    dic_key = f'dic{dic_num}'
    dic = session['dictionaries'][dic_key]
    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_items = list(dic.items())[start:end]
    return jsonify({'tickets': paginated_items, 'total': len(dic)})

@app.route('/search/<int:dic_num>')
def search(dic_num):
    dic_key = f'dic{dic_num}'
    query = request.args.get('query', '').strip()
    dic = session['dictionaries'][dic_key]
    filtered_items = {k: v for k, v in dic.items() if query in k}
    return jsonify({'tickets': list(filtered_items.items()), 'total': len(filtered_items)})

@app.route('/ganador/<int:dic_num>')
def ganador(dic_num):
    dic_key = f'dic{dic_num}'

    if session['winners'].get(dic_key) is not None:
        winner = session['winners'][dic_key]
    else:
        dic = session['dictionaries'][dic_key]
        winner = escoger_numero(dic)
        session['winners'][dic_key] = winner
        session.modified = True  # Ensure the session is saved correctly

    message = message_creation(winner)
    return jsonify({'dic_num': dic_num, 'winner': winner, 'message': message})

@app.route('/regenerar')
def regenerar():
    session.pop('dictionaries', None)
    session.pop('winners', None)
    session['dictionaries'] = {
        'dic1': generar_diccionario(),
        'dic2': generar_diccionario(),
        'dic3': generar_diccionario()
    }
    session['winners'] = {
        'dic1': None,
        'dic2': None,
        'dic3': None
    }
    session.modified = True  # Ensure the session is reset correctly
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)