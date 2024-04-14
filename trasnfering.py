import asyncio
import json
from decimal import Decimal

from db import db

async def main():
    await db.connect()

    file_path = 'halykbank.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for city_info in data:
        for category in city_info['cashback_info']:
            category_name = category['category_name']
            print(category_name)
            category_id = 0
            if category_name != '':
                category_id = await db.fetchval(
                    "INSERT INTO category (category_name) VALUES ($1) RETURNING category_id", category_name)
            # print(category_id)

            #     await db.execute("INSERT INTO category (category_name) VALUES ($1) RETURNING category_id", category_name)
            # category_id = await db.fetchrow()
            # print(category_id)

                for partner in category['stores']:
                    partner_name = partner['store_name']
                    address = partner['store_address']
                    # min_cashback = partner.get('min_cashback', None)
                    max_cashback = partner.get('max_cashback', None)
                    if max_cashback is not None:
                        max_cashback = Decimal(max_cashback.strip('%')) / 100

                    # default_cashback = partner.get('default_cashback', None)

                    partner_id = await db.fetchval("INSERT INTO partners (category_id, partner_name, address) VALUES ($1, $2, $3) RETURNING partner_id", category_id, partner_name, address)
                    await db.execute("INSERT INTO partner_bank (partner_id, bank_id, max_cashback) VALUES ($1, $2, $3)", partner_id, 1, max_cashback)

                    await db.execute("INSERT INTO card_type_cashback (card_type_id, category_id, min_cashback, max_cashback, default_cashback, payment_type_id, partner_id) VALUES($1, $2, $3, $4, $5, $6, $7)", 2, category_id, 0, max_cashback, 0.1, 3, partner_id)
    # Close the connection to the database
    await db.close()

# Run the main function
asyncio.run(main())
