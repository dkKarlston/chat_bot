# actions/menu_actions.py
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionHandleNews(Action):
    def name(self):
        return "action_handle_news"

    def run(self, dispatcher, tracker, domain):
        # Отправляем сообщение с кнопками
        buttons = [
            {"title": "Технологии", "payload": "/ask_news{\"category\":\"tech\"}"},
            {"title": "Спорт", "payload": "/ask_news{\"category\":\"sport\"}"},
            {"title": "Политика", "payload": "/ask_news{\"category\":\"politics\"}"}
        ]

        dispatcher.utter_message(
            text="Выберите категорию новостей:",
            buttons=buttons
        )
        return []