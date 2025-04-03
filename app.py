from flask import Flask, render_template, redirect, url_for, jsonify, request
from numero import generar_diccionario, escoger_numero, message_creation
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inicializar los diccionarios y ganadores en app.config
app.config['DICTIONARIES'] = {}
app.config['WINNERS'] = {}

@app.route('/')
def index():
    if not app.config['DICTIONARIES']:
        new_dictionaries = {
            'dic1': generar_diccionario(),
            'dic2': generar_diccionario(),
            'dic3': generar_diccionario()
        }
        app.config['DICTIONARIES'] = new_dictionaries
        if not app.config.get('WINNERS'):  # <-- Verifica si ya existe antes de regenerar
            app.config['WINNERS'] = {k: escoger_numero(v) for k, v in new_dictionaries.items()}
    return render_template('index.html')

@app.route('/tickets/<int:dic_num>/<int:page>')
def tickets(dic_num, page):
    dic_key = f'dic{dic_num}'
    dic = app.config['DICTIONARIES'][dic_key]
    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_items = list(dic.items())[start:end]
    return jsonify({'tickets': paginated_items, 'total': len(dic)})

@app.route('/search/<int:dic_num>')
def search(dic_num):
    dic_key = f'dic{dic_num}'
    query = request.args.get('query', '').strip()
    dic = app.config['DICTIONARIES'][dic_key]
    filtered_items = {k: v for k, v in dic.items() if query in k}
    return jsonify({'tickets': list(filtered_items.items()), 'total': len(filtered_items)})

@app.route('/ganador/<int:dic_num>')
def ganador(dic_num):
    dic_key = f'dic{dic_num}'
    print("Ganadores actuales:", app.config['WINNERS'])  # <-- Verificar si cambia
    winner = app.config['WINNERS'][dic_key]
    message = message_creation(winner)
    return render_template('ganador.html', dic_num=dic_num, winner=winner, message=message)

@app.route('/regenerar')
def regenerar():
    new_dictionaries = {
        'dic1': generar_diccionario(),
        'dic2': generar_diccionario(),
        'dic3': generar_diccionario()
    }
    app.config['DICTIONARIES'] = new_dictionaries
    app.config['WINNERS'] = {k: escoger_numero(v) for k, v in new_dictionaries.items()}
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)