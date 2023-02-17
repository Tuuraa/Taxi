from sqlalchemy.engine import cursor

from bot.Database.main import async_connect_to_my_sql, create_sync_con


async def exists_user(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "selectcount() from("
            "select from users where user_id = %s"
            "union"
            "select from drivers where user_id = %s",
            (user_id, user_id)
        )
        result = (await cursor.fetchone())[0]
        return bool(result)



