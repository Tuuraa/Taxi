from datetime import date

from bot.Database.main import async_connect_to_my_sql, create_sync_con


async def create_new_user(user_id, full_name, number, link, date_reg):
    conncection, cursor = await async_connect_to_my_sql()

    async with conncection.cursor() as cursor:
        await cursor.execute(
            'insert into users (user_id, full_name, number, link, date_reg, balance) values (%s, %s, %s, %s, %s, %s)',
            (user_id, full_name, number, link, date_reg, 0)
        )

        await conncection.commit()


async def crate_new_driver(user_id, full_name, car, car_number, number, link, date_reg, republic):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'insert into drivers (user_id, full_name, car, car_number, number, link, date_reg, republic, balance) '
            'values (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (user_id, full_name, car, car_number, number, link, date_reg, republic, 0)
        )
        await connection.commit()


async def create_order(user_id, user_location, order_location, distance, amount, republic, date):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'insert into orders (user_id, user_location, order_location, distance, amount, status, republic, date) '
            'values (%s, %s, %s, %s, %s, %s, %s, %s)',
            (user_id, user_location, order_location, distance, amount, 'WAITING', republic, date)
        )

        await connection.commit()


async def create_withdraw(user_id, amount, bank_type, card, date):
    connection, cursor = await async_connect_to_my_sql()

    async with connection.cursor() as cursor:
        await cursor.execute(
            'insert into withdrows (user_id, amount, type_bank, card, date, status) '
            'values (%s, %s, %s, %s, %s, %s) ',
            (user_id, amount, bank_type, card, date, 'WAITING')
        )

        await connection.commit()
