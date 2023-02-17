from bot.Database.main import async_connect_to_my_sql, create_sync_con


async def create_new_user(user_id, name, number, link, date):
    conncection, cursor = await async_connect_to_my_sql()

    async with conncection.cursor() as cursor:
        await cursor.execute(
            'insert into users (user_id, name, number, link, date_reg, date) values (%s,%s, %s, %s, %s, %s)',
        )

        await conncection.commit()


