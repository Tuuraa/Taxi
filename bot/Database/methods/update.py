from bot.Database.main import async_connect_to_my_sql, create_sync_con


async def change_status_to_order(status, id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'update orders set status = %s where id = %s',
            (status, id)
        )

        await connection.commit()