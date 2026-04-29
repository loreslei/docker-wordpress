# from locust import HttpUser, task, between

# class WebsiteUser(HttpUser):
#     wait_time = between(1, 3)

#     @task
#     def cenario_1_imagem_1mb(self):
#         self.client.get("/?p=10", name="Cenário 1: Imagem 1MB")

#     @task
#     def cenario_2_texto_400kb(self):
#         self.client.get("/?p=1", name="Cenário 2: Texto 400kb")

#     @task
#     def cenario_3_imagem_300kb(self):
#         self.client.get("/?p=7", name="Cenário 3: Imagem 300kb")

import os
from locust import HttpUser, task, between

# O script lerá qual cenário deve ser executado (1, 2, 3 ou TODOS)
CENARIO = os.getenv("CENARIO", "TODOS")

def cenario_1(user):
    user.client.get("/?p=10", name="Cenário 1: Imagem 1MB")

def cenario_2(user):
    user.client.get("/?p=1", name="Cenário 2: Texto 400kb")

def cenario_3(user):
    user.client.get("/?p=7", name="Cenário 3: Imagem 300kb")

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    # Monta a matriz de ataque dependendo da ordem do arquivo .bat
    if CENARIO == "1":
        tasks = [cenario_1]
    elif CENARIO == "2":
        tasks = [cenario_2]
    elif CENARIO == "3":
        tasks = [cenario_3]
    else:
        # Se for "TODOS", executa os três posts misturados
        tasks = [cenario_1, cenario_2, cenario_3]