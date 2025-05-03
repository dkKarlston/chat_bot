import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List, Text, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

DB_PATH = "memory.db"


# region Database Utilities
def init_db() -> None:
    """Инициализац структуры базы данных"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_memory (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                favorite_topic TEXT,
                last_seen TEXT,
                extra TEXT
            );
        """)
        conn.commit()


def db_execute(
        query: str,
        params: tuple = (),
        commit: bool = False
) -> Optional[sqlite3.Cursor]:
    """Универсальный метод для выполнения запросов"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def upsert_user(
        user_id: str,
        name: Optional[str],
        topic: Optional[str],
        extra: Optional[Dict] = None
) -> bool:
    """Обновление или создание записи пользователя"""
    extra_data = json.dumps(extra) if extra else "{}"
    result = db_execute(
        """
        INSERT INTO user_memory(user_id, name, favorite_topic, last_seen, extra)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            favorite_topic = excluded.favorite_topic,
            last_seen = excluded.last_seen,
            extra = excluded.extra
        """,
        (user_id, name, topic, datetime.utcnow().isoformat(), extra_data),
        commit=True
    )
    return result is not None


def get_user(user_id: str) -> Optional[tuple]:
    """Получение данных пользователя"""
    cursor = db_execute(
        "SELECT name, favorite_topic, extra FROM user_memory WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchone() if cursor else None


# endregion

class BaseDBAction(Action):
    """Базовый класс для действий с БД"""

    def _get_user_id(self, tracker: Tracker) -> str:
        """Валидация идентификатора пользователя"""
        user_id = tracker.sender_id
        if not user_id or len(user_id) < 5:
            raise ValueError("Invalid user ID")
        return user_id


class ActionSaveUserMemory(BaseDBAction):
    def name(self) -> Text:
        return "action_save_user_memory"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        try:
            user_id = self._get_user_id(tracker)
            success = upsert_user(
                user_id=user_id,
                name=tracker.get_slot("name"),
                topic=tracker.get_slot("favorite_topic"),
                extra={}  # Здесь можно добавить дополнительные данные
            )

            if success:
                dispatcher.utter_message(text="Данные успешно сохранены!")
            else:
                dispatcher.utter_message(text="Ошибка сохранения данных")

        except Exception as e:
            dispatcher.utter_message(text="Произошла внутренняя ошибка")
            print(f"Error in ActionSaveUserMemory: {e}")

        return []


class ActionLoadUserMemory(BaseDBAction):
    def name(self) -> Text:
        return "action_load_user_memory"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        events = []
        try:
            user_id = self._get_user_id(tracker)
            user_data = get_user(user_id)

            if user_data:
                name, topic, extra_json = user_data
                greeting = f"С возвращением{', ' + name if name else ''}!"
                dispatcher.utter_message(text=greeting)

                # Обновление слотов
                events.extend([
                    SlotSet("name", name),
                    SlotSet("favorite_topic", topic)
                ])
            else:
                dispatcher.utter_message(text="Привет! Давайте познакомимся.")

        except Exception as e:
            dispatcher.utter_message(text="Ошибка загрузки данных")
            print(f"Error in ActionLoadUserMemory: {e}")

        return events



