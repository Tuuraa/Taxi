from bot.Database.main import async_connect_to_my_sql, create_sync_con


async def create_new_user(user_id, full_name, number, link, date_reg):
    conncection, cursor = await async_connect_to_my_sql()

    async with conncection.cursor() as cursor:
        await cursor.execute(
            'insert into users (user_id, full_name, number, link, date_reg) values (%s,%s, %s, %s, %s)',
            (user_id, full_name, number, link, date_reg)
        )

        await conncection.commit()


async def crate_new_driver(user_id, full_name, car, car_number, number, link, date_reg):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'insert into drivers (user_id, full_name, car, car_number, number, link, date_reg) values (%s, %s, %s, %s, %s, %s, %s)',
            (user_id, full_name, car, car_number, number, link, date_reg)
        )
        await connection.commit()
