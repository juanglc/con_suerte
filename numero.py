from random import choices, sample
from datetime import datetime

def generar_numero():
    numero_gen = choices(range(10), k=4)
    return numero_gen

def generar_diccionario():
    diccionario = {}
    while len(diccionario) < 10000:
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
    return winner_key

def message_creation(winner_key, winner_value):
    print(winner_key)
    if winner_value['estado'] == 0:
        return f"El número ganador {winner_key} no fue comprado, por lo que el premio no se distribuye"
    else:
        return f"El número ganador {winner_key} fue comprado, por lo que el premio se distribuye"

def get_winner(dic):
    num = escoger_numero(dic)
    print(num)
    return num