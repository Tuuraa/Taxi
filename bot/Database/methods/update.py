from bot.Database.main import async_connect_to_my_sql, create_sync_con


async def change_status_to_order(status, id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update orders set status = %s where id = %s',
            (status, id)
        )

        await connection.commit()


async def add_top_up(user_id, amount):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update users set balance = balance + %s where user_id = %s',
            (amount, user_id)
        )

        await connection.commit()


async def change_region(user_id, republic):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update drivers set republic = %s where user_id = %s',
            (republic, user_id)
        )

        await connection.commit()


async def change_complete_order(date, id_order):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update orders set compete_date = %s where id = %s',
            (date, id_order)
        )

        await connection.commit()


async def add_coefficient(coefficient, user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update drivers set coefficient = coefficient + %s where user_id = %s',
            (coefficient, user_id)
        )

        await connection.commit()


async def remove_balance_from_user(balance, user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update users set balance = balance - %s where user_id = %s', (balance, user_id)
        )

        await connection.commit()


async def add_balance_from_driver(balance, driver_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update drivers set balance = balance + %s where user_id = %s', (balance, driver_id)
        )

        await connection.commit()

