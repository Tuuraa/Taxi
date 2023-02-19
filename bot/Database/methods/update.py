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


async def change_region(user_id, region):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update drivers set region = %s where user_id = %s',
            (user_id, region)
        )

        await connection.commit()