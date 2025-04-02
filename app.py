from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_session import Session
from numero import generar_diccionario, escoger_numero, message_creation
import os
import shutil

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_sessions'  # Directorio para sesiones
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# **Elimina las sesiones previas al iniciar el servidor**
if os.path.exists(app.config['SESSION_FILE_DIR']):
    shutil.rmtree(app.config['SESSION_FILE_DIR'])  # Borra todas las sesiones previas
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)  # Vuelve a crear la carpeta vacía

@app.before_request
def initialize_session():
    """ Reinicia los valores de la sesión cuando se inicia el servidor. """
    if 'initialized' not in session:
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
        session['initialized'] = True  # Marca que la sesión ha sido iniciada correctamente
        session.modified = True

@app.route('/')
def index():
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
        session.modified = True

    message = message_creation(winner)
    return render_template('ganador.html', dic_num=dic_num, winner=winner, message=message)

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
    session.modified = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)