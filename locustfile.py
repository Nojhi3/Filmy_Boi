from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def send_message(self):
        response = self.client.post(
            "/api/chat/",
            json={"character": "jules winnfield", "user_message": "Say what again!"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Chat API responded correctly!")
        else:
            print(f"❌ Failed! Status Code: {response.status_code}")

