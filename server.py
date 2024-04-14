from decimal import Decimal
from sanic_cors import CORS
from sanic import Sanic, response
from sanic.response import html
import bcrypt
from jinja2 import Environment, FileSystemLoader
import re
from sanic import response



app = Sanic(__name__)
cors = CORS(app)
USERNAME_REGEX = r'^[a-zA-Z0-9]+$'
from db import db


@app.before_server_start
async def before_server_start(*args, **kwargs):
    await db.connect()


@app.before_server_stop
async def before_server_stop(*args, **kwargs):
    await db.close()


env = Environment(loader=FileSystemLoader('templates'))



@app.route("/")
async def index(request):
    template = env.get_template('./map.html')

    return response.html(template.render())

@app.route('/login', methods=['POST', 'GET'])
async def login(request):
    if request.method == 'GET':
        template = env.get_template('./login.html')
        return response.html(template.render())

    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return response.json({'message': 'Username or password is missing'}, status=400)

    user = await db.fetchrow('SELECT * FROM users WHERE username = $1', username)

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return response.redirect('/')

@app.route('/register', methods=['GET', 'POST'])
async def register_user(request):
    if request.method == 'GET':
        template = env.get_template('./register.html')

        return response.html(template.render())

    data = request.form

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')


    if not username or not re.match(USERNAME_REGEX, username):
        return response.text('Invalid username', status=400)

    if not password or len(password) < 8:
        return response.text('Password is short', status=400)

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')
    except Exception as e:
        return response.text('Error hashing password', status=500)


    user_exist = await db.fetchval('SELECT COUNT(*) FROM users WHERE username = $1', username)
    if user_exist:
        return response.text('username already exist', status=400)

    try:
        await db.execute('INSERT INTO users (username, email, password, phone) VALUES ($1, $2, $3, $4)', username, email,
                           hashed_password_str, phone)
    except Exception as e:
        print(f'Error inserting user into database: {e}')
        return response.text('Error registering user', status=500)

    return response.redirect('./login')


@app.route('/logout', methods=['GET'])
async def logout(request):
    response_obj = response.redirect('/login')
    return response_obj


@app.route('/banks', methods=['GET'])
async def banks(request):
    response_obj = response.redirect('/login')


from sanic import response

from sanic import response

@app.route('/mapping', methods=['GET'])
async def mapping(request):
    rows = await db.fetch('SELECT * FROM cart_type')
    if rows:
        data = [dict(row.items()) for row in rows]
        for row in data:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        return response.json(data)
    else:
        return response.text("No data found", status=404)



@app.route('/cards', methods=['POST'])
async def cards(request):
    # global mapping_data
    # if mapping_data:
    #     return response.json(mapping_data)
    # else:
    #     return response.text("Mapping data is empty", status=404)
    for row in request.json:
        userId = row['user_id']
        cardId = row['cart_type_id']
        print(userId, cardId)
        await db.execute("INSERT INTO card_type_user(card_type_id, user_id) VALUES ($1, $2)", cardId, userId)

    return response.json({"success": True})

@app.route('/categories', methods=['GET'])
async def categories(request):
    rows = await db.fetch('SELECT * FROM category')
    if rows:
        data = [dict(row.items()) for row in rows]
        for row in data:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        return response.json(data)
    else:
        return response.text("No data found", status=404)


from sanic import request, response


@app.route('/category', methods=['POST'])
async def category(request):
    category_name = request.args.get('category_name')
    if category_name:
        result = await db.fetch('''
            SELECT ctc.*, p.partner_id, p.partner_name, p.address
            FROM card_type_cashback AS ctc
            JOIN partners AS p ON ctc.partner_id = p.partner_id
            WHERE ctc.category_id IN (
                SELECT category_id FROM category WHERE category_name = $1
            )
        ''', category_name)

        if result:
            data = [dict(row.items()) for row in result]
            for item in data:
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
            return response.json(data)
        else:
            return response.text("Category data not found", status=404)
    else:
        return response.text("Category name not provided", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
