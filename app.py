# import json

# def lambda_handler(event, context):
#     return {
#         'statusCode': 200,
#         'body': json.dumps({"message": "Hello, DevSecOps!"})
#     }

import os
import pickle
import subprocess
import hashlib

# HARD-CODED SECRET (Para demostrar hallazgo de credenciales en Bandit)
SECRET_KEY = "12345-super-secret-key"

# Función insegura que construye un comando con shell=True (posible injection)
def insecure_shell(user_input):
    cmd = f"echo {user_input} | grep TODO"
    # Bandit B602: shell=True es inseguro porque puede permitir inyección de comandos
    subprocess.run(cmd, shell=True)

# Función insegura que evalúa código en tiempo de ejecución
def eval_function(code_str):
    # Bandit B307: uso de eval es inseguro
    eval(code_str)

# Deserialización insegura con pickle
def insecure_deserialization(pickled_data):
    # Bandit B301: uso de pickle (deserialización insegura)
    return pickle.loads(pickled_data)

# Uso de algoritmo de hash inseguro
def md5_password(password):
    # Bandit B303: uso de hashlib.md5 (no seguro para contraseñas)
    return hashlib.md5(password.encode()).hexdigest()

# Simulación de handler para Lambda o Flask
def lambda_handler(event, context):
    user_input = event.get("user_input", "default_todo")
    code_str = event.get("code_str", "print('hello from eval')")
    pickled_data = event.get("pickled_data", None)

    # Llamamos funciones inseguras
    insecure_shell(user_input)
    eval_function(code_str)
    if pickled_data:
        insecure_deserialization(pickled_data)

    hashed_pass = md5_password("dummy-password")
    return {
        "statusCode": 200,
        "body": f"Insecure code triggered.\nMD5 of dummy-password: {hashed_pass}\nSecret key: {SECRET_KEY}"
    }
