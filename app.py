from flask import Flask, render_template, redirect, url_for, jsonify, request, session
from flask_session import Session
from numero import generar_diccionario, escoger_numero, message_creation
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de la sesión
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Inicializar la extensión de sesión
Session(app)

def initialize_data():
    if 'dictionaries' not in session:
        session['dictionaries'] = {
            'dic1': generar_diccionario(),
            'dic2': generar_diccionario(),
            'dic3': generar_diccionario()
        }

    if 'winners' not in session:
        session['winners'] = {}
        for dic_key in session['dictionaries']:
            session['winners'][dic_key] = escoger_numero(session['dictionaries'][dic_key])

@app.route('/')
def index():
    initialize_data()
    return render_template('index.html')

@app.route('/tickets/<int:dic_num>/<int:page>')
def tickets(dic_num, page):
    initialize_data()
    dic_key = f'dic{dic_num}'

    if dic_key not in session['dictionaries']:
        return jsonify({'error': 'Diccionario no encontrado'}), 404

    dic = session['dictionaries'][dic_key]
    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_items = list(dic.items())[start:end]

    return jsonify({'tickets': paginated_items, 'total': len(dic)})

@app.route('/search/<int:dic_num>', defaults={'page': 1})
@app.route('/search/<int:dic_num>/<int:page>')
def search(dic_num, page):
    dic_key = f'dic{dic_num}'
    query = request.args.get('query', '').strip()
    dic = session['dictionaries'][dic_key]
    filtered_items = {k: v for k, v in dic.items() if query in k}

    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_items = list(filtered_items.items())[start:end]

    return jsonify({'tickets': paginated_items, 'total': len(filtered_items)})

@app.route('/ganador/<int:dic_num>')
def ganador(dic_num):
    initialize_data()
    dic_key = f'dic{dic_num}'
    winner_key = session['winners'][dic_key]
    winner_value = session['dictionaries'][dic_key][winner_key]
    message = message_creation(winner_key, winner_value)
    return render_template('ganador.html', dic_num=dic_num, winner=(winner_key, winner_value), message=message)

@app.route('/regenerar')
def regenerar():
    session.pop('dictionaries', None)
    session.pop('winners', None)
    initialize_data()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)