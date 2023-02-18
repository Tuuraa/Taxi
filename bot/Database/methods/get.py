from sqlalchemy.engine import cursor

from bot.Database.main import async_connect_to_my_sql, create_sync_con


async def exists_passenger(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:

        await cursor.execute('select * from users where user_id = %s', user_id)

        result = (await cursor.fetchone())
        return bool(result)


async def exists_driver(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:

        await cursor.execute('select * from drivers where user_id = %s', user_id)

        result = (await cursor.fetchone())
        return bool(result)


async def profile_data(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'select user_id, full_name, number from users where user_id = %s',
            user_id
        )
        result = await cursor.fetchone()

        if result:
            return 'pass', result
        else:
            await cursor.execute(
                'select user_id, full_name, number, car, car_number from drivers where user_id = %s',
                user_id
            )

            result = await cursor.fetchone()
            return 'drive', result


async def type_user(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'select user_id, full_name, number from users where user_id = %s',
            user_id
        )
        result = await cursor.fetchone()

        if result:
            return 'passenger'
        else:
            return 'driver'


async def republic_by_driver(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'select republic from drivers where user_id = %s',
            user_id
        )

        result = await cursor.fetchone()
        return result[0]


async def all_active_orders(republic):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from orders where status = 'WAITING' and republic = %s",
            republic
        )

        result = await cursor.fetchall()
        return result
