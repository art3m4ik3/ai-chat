from g4f.client import Client


class ChatGPTService:
    def __init__(self):
        self.client = Client()
        self.initial_greeting = (
            "Привет! Чем могу помочь? Я готов ответить на любые ваши вопросы."
        )

    def get_initial_greeting(self):
        return self.initial_greeting

    def generate_response(self, messages):
        try:
            user_message = messages[-1]["content"]

            response = self.client.chat.completions.create(
                model="",
                messages=[{"role": "user", "content": user_message}],
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


chat_service = ChatGPTService()
