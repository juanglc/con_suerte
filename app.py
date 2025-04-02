from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_session import Session
from numero import generar_diccionario, escoger_numero, message_creation
import os
import redis

# Configurar Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")  # Cambia esto con tu URL de Redis en producción
redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

# Verificar conexión a Redis
def check_redis_connection():
    try:
        redis_client.ping()
        print("Conectado a Redis exitosamente")
    except redis.ConnectionError:
        print("Error: No se pudo conectar a Redis")
        exit(1)

check_redis_connection()

def reset_session():
    redis_client.flushdb()  # Reinicia los valores de la sesión limpiando Redis

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis_client

Session(app)

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
    return render_template('ganador.html', dic_num=dic_num, winner=winner, message=message)

@app.route('/regenerar')
def regenerar():
    reset_session()  # Limpia Redis completamente
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
