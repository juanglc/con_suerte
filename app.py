from flask import Flask, render_template, redirect, url_for, jsonify, request
from numero import generar_diccionario, escoger_numero, message_creation
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Diccionario global para almacenar los diccionarios y los ganadores
data = {
    'dictionaries': {},
    'winners': {}
}

def initialize_data():
    if not data['dictionaries']:  # Solo se generan si aún no existen
        data['dictionaries'] = {
            'dic1': generar_diccionario(),
            'dic2': generar_diccionario(),
            'dic3': generar_diccionario()
        }

    if not data['winners']:  # Solo se asignan ganadores si no existen
        for dic_key in data['dictionaries']:
            if dic_key not in data['winners']:
                data['winners'][dic_key] = escoger_numero(data['dictionaries'][dic_key])

@app.route('/')
def index():
    initialize_data()
    return render_template('index.html')

@app.route('/tickets/<int:dic_num>/<int:page>')
def tickets(dic_num, page):
    initialize_data()
    dic_key = f'dic{dic_num}'

    # Nos aseguramos de que el diccionario ya existe antes de acceder
    if dic_key not in data['dictionaries']:
        return jsonify({'error': 'Diccionario no encontrado'}), 404

    dic = data['dictionaries'][dic_key]
    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_items = list(dic.items())[start:end]

    return jsonify({'tickets': paginated_items, 'total': len(dic)})

@app.route('/search/<int:dic_num>')
def search(dic_num):
    initialize_data()
    dic_key = f'dic{dic_num}'
    query = request.args.get('query', '').strip()
    dic = data['dictionaries'][dic_key]
    filtered_items = {k: v for k, v in dic.items() if query in k}
    return jsonify({'tickets': list(filtered_items.items()), 'total': len(filtered_items)})

@app.route('/ganador/<int:dic_num>')
def ganador(dic_num):
    initialize_data()
    dic_key = f'dic{dic_num}'
    winner_key = data['winners'][dic_key]
    winner_value = data['dictionaries'][dic_key][winner_key]
    message = message_creation(winner_key, winner_value)
    return render_template('ganador.html', dic_num=dic_num, winner=(winner_key, winner_value), message=message)

@app.route('/regenerar')
def regenerar():
    data['dictionaries'].clear()
    data['winners'].clear()
    initialize_data()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)