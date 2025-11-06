from locust import HttpUser, task, between
import random, string

def random_email():
    return f"user_{''.join(random.choices(string.ascii_lowercase, k=5))}@test.com"

class QuantSimUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        email = random_email()
        self.client.post("/auth/signup", json={"email": email, "password": "pass123"})
        resp = self.client.post("/auth/login", json={"email": email, "password": "pass123"})
        self.token = resp.json().get("access_token")

    @task(3)
    def run_simulation(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"command": "AAPL-L-100% 2020-01-01 2020-12-31"}
        self.client.post("/simulate/async", json=payload, headers=headers)

    @task(1)
    def get_metrics(self):
        self.client.get("/metrics")
