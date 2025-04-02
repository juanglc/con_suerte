from flask import Flask, render_template, redirect, url_for, jsonify, request
from numero import generar_diccionario, escoger_numero, message_creation
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Diccionario global para almacenar los diccionarios y los ganadores
data = {
    'dictionaries': {
        'dic1': generar_diccionario(),
        'dic2': generar_diccionario(),
        'dic3': generar_diccionario()
    },
    'winners': {}
}

# Generar ganadores al iniciar
for dic_key in data['dictionaries']:
    data['winners'][dic_key] = escoger_numero(data['dictionaries'][dic_key])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tickets/<int:dic_num>/<int:page>')
def tickets(dic_num, page):
    dic_key = f'dic{dic_num}'
    dic = data['dictionaries'][dic_key]
    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_items = list(dic.items())[start:end]
    return jsonify({'tickets': paginated_items, 'total': len(dic)})

@app.route('/search/<int:dic_num>')
def search(dic_num):
    dic_key = f'dic{dic_num}'
    query = request.args.get('query', '').strip()
    dic = data['dictionaries'][dic_key]
    filtered_items = {k: v for k, v in dic.items() if query in k}
    return jsonify({'tickets': list(filtered_items.items()), 'total': len(filtered_items)})

@app.route('/ganador/<int:dic_num>')
def ganador(dic_num):
    dic_key = f'dic{dic_num}'
    winner = data['winners'][dic_key]
    message = message_creation(winner)
    return render_template('ganador.html', dic_num=dic_num, winner=winner, message=message)

@app.route('/regenerar')
def regenerar():
    data['dictionaries'] = {
        'dic1': generar_diccionario(),
        'dic2': generar_diccionario(),
        'dic3': generar_diccionario()
    }
    data['winners'] = {}
    for dic_key in data['dictionaries']:
        data['winners'][dic_key] = escoger_numero(data['dictionaries'][dic_key])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)