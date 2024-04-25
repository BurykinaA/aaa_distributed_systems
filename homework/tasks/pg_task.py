from dataclasses import dataclass

import asyncpg


@dataclass
class ItemEntry:
    item_id: int
    user_id: int
    title: str
    description: str


class ItemStorage:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # We initialize client here, because we need to connect it,
        # __init__ method doesn't support awaits.
        #
        # Pool will be configured using env variables.
        self._pool = await asyncpg.create_pool()

    async def disconnect(self) -> None:
        # Connections should be gracefully closed on app exit to avoid
        # resource leaks.
        await self._pool.close()

    async def create_tables_structure(self) -> None:
        """
        Создайте таблицу items со следующими колонками:
         item_id (int) - обязательное поле, значения должны быть уникальными
         user_id (int) - обязательное поле
         title (str) - обязательное поле
         description (str) - обязательное поле
        """
        query = """
        CREATE TABLE IF NOT EXISTS items (
            item_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        );
        """
        async with self._pool.acquire() as connection:
            await connection.execute(query)

    async def save_items(self, items: list[ItemEntry]) -> None:
        """
        Напишите код для вставки записей в таблицу items одним запросом, цикл
        использовать нельзя.
        """
        query = """
        INSERT INTO items (item_id, user_id, title, description)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (item_id) DO NOTHING;
        """
        values = [
            (item.item_id, item.user_id, item.title, item.description) for item in items
        ]
        async with self._pool.acquire() as connection:
            await connection.executemany(query, values)

    async def find_similar_items(
        self, user_id: int, title: str, description: str
    ) -> list[ItemEntry]:
        """
        Напишите код для поиска записей, имеющих указанные user_id, title и description.
        """
        query = """
        SELECT item_id, user_id, title, description
        FROM items
        WHERE user_id = $1 AND title = $2 AND description = $3;
        """
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(query, user_id, title, description)
        return [
            ItemEntry(row["item_id"], row["user_id"], row["title"], row["description"])
            for row in rows
        ]
