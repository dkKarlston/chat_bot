from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
DB_PATH = "memory.db"


def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            favorite_topic TEXT,
            last_seen TEXT,
            extra TEXT
        )
    """)
    conn.commit()
    conn.close()


class ActionSaveUserMemory(Action):
    """Сохранение данных пользователя в БД"""

    def name(self) -> str:
        return "action_save_user_memory"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        init_db()
        user_id = tracker.sender_id
        name = tracker.get_slot("name")
        topic = tracker.get_slot("favorite_topic")
        extra_data = {}  # Дополнительные данные (можно расширить)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_memory(user_id, name, favorite_topic, last_seen, extra)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    favorite_topic = excluded.favorite_topic,
                    last_seen = excluded.last_seen,
                    extra = excluded.extra
            """, (user_id, name, topic, datetime.utcnow().isoformat(), json.dumps(extra_data)))
            conn.commit()
            dispatcher.utter_message(text="Данные успешно сохранены!")

        except sqlite3.Error as e:
            logger.error(f"Ошибка базы данных: {e}")
            dispatcher.utter_message(text="Ошибка при сохранении данных")

        finally:
            if conn:
                conn.close()

        return []


class ActionLoadUserMemory(Action):
    """Загрузка данных пользователя из БД"""

    def name(self) -> str:
        return "action_load_user_memory"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        events = []
        conn = None
        try:
            user_id = tracker.sender_id
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Проверяем существование таблицы
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='user_memory'
            """)
            if not cursor.fetchone():
                raise Exception("Таблица user_memory не найдена")

            cursor.execute("SELECT name, favorite_topic FROM user_memory WHERE user_id=?", (user_id,))
            row = cursor.fetchone()

            if row:
                name, topic = row
                events = [
                    SlotSet("name", name),
                    SlotSet("favorite_topic", topic)
                ]
                dispatcher.utter_message(text=f"С возвращением, {name}!")
            else:
                events = [
                    SlotSet("name", None),
                    SlotSet("favorite_topic", None)
                ]
                dispatcher.utter_message(text="Привет! Давайте познакомимся.")

        except sqlite3.Error as e:
            logger.error(f"Ошибка базы данных: {e}")
            dispatcher.utter_message(text="Ошибка при загрузке данных")

        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            dispatcher.utter_message(text="Внутренняя ошибка системы")

        finally:
            if conn:
                conn.close()

        return events