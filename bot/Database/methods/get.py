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
            'select user_id, full_name, number, balance from users where user_id = %s',
            user_id
        )
        result = await cursor.fetchone()

        if result:
            return 'pass', result
        else:
            await cursor.execute(
                'select user_id, full_name, number, car, car_number, republic, balance from drivers where user_id = %s',
                user_id
            )

            result = await cursor.fetchone()
            return 'drive', result


async def balance_by_driver(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'select balance from drivers where user_id = %s', user_id
        )
        result = await cursor.fetchone()
        return result[0]


async def balance_by_user(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'select balance from users where user_id = %s', user_id
        )
        result = await cursor.fetchone()
        return result[0]


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


async def information_by_user(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from users where user_id = %s",
            user_id
        )

        result = await cursor.fetchone()
        return result


async def information_by_driver(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from drivers where user_id = %s",
            user_id
        )

        result = await cursor.fetchone()
        return result


async def orders_by_status_and_republic(republic, status):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from orders where status = %s and republic = %s",
            (status, republic)
        )

        result = await cursor.fetchall()
        return result


async def information_by_order(id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from orders where id = %s", id
        )

        result = await cursor.fetchone()
        return result


async def all_drivers(user_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select user_id from drivers where republic = %s",
            user_id
        )

        result = await cursor.fetchone()
        return result


async def all_withdraws():
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from withdrows where status = 'WAITING'"
        )

        result = await cursor.fetchall()
        return result


async def all_drivers_by_republic(republic):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select user_id from drivers where republic = %s", republic
        )

        result = await cursor.fetchall()
        return result


async def check_user_from_order(user_id, status="PROCESSING"):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from orders where user_id = %s and status = %s",
        (user_id, status))

        result = await cursor.fetchall()
        return bool(result)


async def check_status_in_place(user_id, status="INPLACE"):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from orders where user_id = %s and status = %s",
        (user_id, status))

        result = await cursor.fetchall()
        return bool(result)


async def check_status_to_waiting(user_id, status="WAITING"):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select * from orders where user_id = %s and status = %s",
        (user_id, status))

        result = await cursor.fetchall()
        return bool(result)


async def get_status_from_order(order_id):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            "select status from orders where id = %s", order_id
        )

        result = await cursor.fetchone()
        return result
