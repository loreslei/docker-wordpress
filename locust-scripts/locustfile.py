from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def cenario_1_imagem_1mb(self):
        self.client.get("/?p=11", name="Cenário 1: Imagem 1MB")

    @task
    def cenario_2_texto_400kb(self):
        self.client.get("/?p=17", name="Cenário 2: Texto 400kb")

    @task
    def cenario_3_imagem_300kb(self):
        self.client.get("/?p=14", name="Cenário 3: Imagem 300kb")