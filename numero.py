from random import sample, choices
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

def imprimir_diccionario(dicc):
    for i in sorted(dicc.keys()):
        print(f"{i}: {dicc[i]}")

def escoger_numero(diccionario):
       # Asegúrate de que el método de selección del ganador sea consistente
       # Por ejemplo, ordenar las claves y seleccionar la primera
       return sorted(diccionario.items(), key=lambda x: x[1])[0]

def get_key(dic):
    return list(dic.keys())

def message_creation(winner):
    if winner[1]['estado'] == 0:
        message = f"El número {winner[0]} no fue comprado, por lo cual el premio no será repartido."
        print(message)
    else:
        message = f"El número {winner[0]} fue comprado, por lo cual el premio será repartido al ganador."
        print(message)
    return message