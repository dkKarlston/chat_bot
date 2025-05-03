import webbrowser
from argparse import Action
from ast import literal_eval
from datetime import datetime
from random import random
from tkinter import Text
from typing import Dict, Any, List

from rasa_sdk import Tracker, logger
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import datetime
import random

FACTS = {
    "спорт": [
        "Бадминтон – является самым быстрым ракеточным видом спорта: скорость полета волана может достигать в среднем "
        "270 км/час.",
        "В стандартном мячике для гольфа всего 336 выемок.",
        "В пелотоне Формулы-1 нет болида под номером 13, после 12-го сразу идёт 1",
        "Фернандо Алонсо, гонщик «Формулы-1», сел за руль карта в три года.",
        "Нильс Бор, знаменитый физик, был вратарём сборной Дании.",
    ],
    "история": [
        "Великая китайская стена не видна с Луны невооруженным глазом.",
        "Первая фотография была сделана в 1826 году.",
        "Рим был основан в 753 году до нашей эры.",
        "Петр».",
        "Арабские цифры изобрелись не арабами, а математиками из Индии.",
        "Когда-то морфин использовался для уменьшения кашля.",
    ],
    "космос": [
        "Температура на поверхности Венеры достигает 465°C, что горячее, чем на Меркурии, хотя Венера дальше от Солнца.",
        "Самая высокая гора в Солнечной системе - гора Олимп на Марсе. Ее высота достигает 21 километр.",
        "Нейтронные звезды могут вращаться со скоростью до 600 оборотов в секунду.",
        "В космосе нельзя заплакать. В условиях микрогравитации слезы не падают вниз, как на Земле, а остаются на "
        "глазах в виде маленьких капель.",
        "В космосе нет звука. Звук не может распространяться в вакууме, так как ему нужны молекулы воздуха или "
        "другого вещества для передачи волн.",
        "Сатурн может плавать в воде. Если бы существовал бассейн с водой достаточного размера, Сатурн, из-за своей "
        "низкой плотности, плавал бы на поверхности.",
    ],
}


def name() -> str:
    return "action_get_time"


class ActionGetTime(Action):

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        try:

            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%d.%m.%Y")

            message = f"Сейчас {current_time}, сегодня {current_date}"
            dispatcher.utter_message(text=message)

            return []

        except Exception as e:
            dispatcher.utter_message(text="Не удалось определить время.")
            logger.error(f"Error in action_get_time: {e}")
            return []  # Всегда возвращаем список, даже при ошибке


class ActionTellFact(Action):
    def name(self) -> str:
        return "action_tell_fact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> list[dict[str, Any]]:
        category = tracker.get_slot("category")
        if not category or category not in FACTS:
            dispatcher.utter_message(text="Пожалуйста, выберите категорию: спорт, история или космос.")
            return [SlotSet("category", None)]

        fact = random.choice(FACTS[category])
        dispatcher.utter_message(text=fact)
        return [SlotSet("category", None)]


class ActionSearchWeb(Action):
    def name(self) -> str:
        return "action_search_web"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = tracker.get_slot("query")
        if not query:
            dispatcher.utter_message(text="Что вы хотите найти?")
            return []

        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open_new_tab(url)
            dispatcher.utter_message(text=f"Ищу '{query}' в Google...")
        except Exception as e:
            dispatcher.utter_message(text="Не удалось выполнить поиск")

        return []


class ActionCalculate(Action):
    from ast import literal_eval
    def name(self) -> str:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> list[Any] | list[dict[str, Any]]:

        expression = tracker.get_slot("expression")
        if not expression:
            dispatcher.utter_message(text="Пожалуйста, введите выражение для вычисления.")
            return []

        try:
            expression = expression.replace('x', '*').replace('^', '**')
            result = literal_eval(expression)
            dispatcher.utter_message(text=f"Результат: {result}")
        except (SyntaxError, TypeError, NameError, ZeroDivisionError):
            dispatcher.utter_message(text="Не могу вычислить это выражение.")

        return [SlotSet("expression", None)]


class ActionAnalyzeMood(Action):
    def name(self) -> str:
        return "action_analyze_mood"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text", "").lower()

        positive_words = ["хорошо", "отлично", "прекрасно", "радост", "счастлив", "ура", "люблю", "классно",
                          "замечательно"]
        negative_words = ["плохо", "ужасно", "грустно", "несчаст", "тоскливо", "разочарован", "устал", "бесит"]

        positive_count = sum(word in user_message for word in positive_words)
        negative_count = sum(word in user_message for word in negative_words)

        if positive_count > negative_count:
            mood = "positive"
        elif negative_count > positive_count:
            mood = "negative"
        else:
            mood = "neutral"

        responses = {
            "positive": [
                "Ты звучишь очень позитивно! 😄 Чем могу порадовать тебя ещё?",
                "Похоже, у вас отличное настроение!",
                "Я чувствую вашу радость! Так держать!"
            ],
            "negative": [
                "Ты, похоже, не в настроении... 😔 Хочешь поговорить об этом?",
                "Кажется, вам сейчас нелегко...",
                "Ваше настроение кажется подавленным. Если нужно поговорить - я здесь."
            ],
            "neutral": [
                "Улавливаю нейтральный настрой. Спрашивай, если что-нибудь нужно!",
                "Ваше настроение кажется ровным. Все в порядке?",
                "Похоже, у вас обычный день. Надеюсь, он станет еще лучше!"
            ]
        }

        dispatcher.utter_message(text=random.choice(responses[mood]))
        return []
