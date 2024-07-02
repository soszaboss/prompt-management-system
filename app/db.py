import os
import dotenv
from getpass import getpass
import psycopg
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash
import click
from flask import current_app, g

dotenv.load_dotenv()

def get_db():

    '''
        g is a special object that is unique for each request.
        It is used to store data that might be accessed by multiple functions during the request.
        The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
    '''

    if 'db' not in g:
        g.db = psycopg.connect(current_app.config['DATABASE'], row_factory=dict_row, autocommit=True)

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():

    '''
        open_resource() opens a file relative to the app package,
        which is useful since you won’t necessarily know where that location is when deploying the application later.
        get_db returns a database connection, which is used to execute the commands read from the file
    '''

    conn = get_db()

    with current_app.open_resource('schema.sql') as f:
        with conn.cursor() as cur:
            cur.execute(f.read().decode('utf8'))
            conn.commit()


#click.command() defines a command line command called init-db that calls the init_db function and shows a success message to the user.
# You can read Command Line Interface to learn more about writing commands.
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


import re

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def validate_password(password):
    '''
        regex pattern that checks if a password meets the following requirements:

        At least 12 characters in length.
        Contains at least one uppercase letter.
        Contains at least one lowercase letter.
        Contains at least one digit (number).
        Contains at least one special character (e.g., !, @, #, $, %, etc.).
    '''
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&*])[A-Za-z\d@#$%^&*]{12,}$"
    return bool(re.match(pattern, password))

def user_input(field: str, password:bool=False) -> str:
    """
    Prompt the user for input and validate it.

    Args:
        field (str): The field name (e.g., 'username', 'email').

    Returns:
        str: The validated user input.
    """
    while True:
        if password:
            result = getpass(prompt=f'{field}: ')
            if not result:
                result = getpass(prompt=f'{field}: ')
            else:
                return result
        else:
            result = input(f'{field} : ').strip()
            if not result:
                result = input(f'{field} : ').strip()
            else:
                if field == 'username':
                    db = get_db()
                    exist = db.execute("SELECT u.username FROM users u WHERE u.username = %s;", (result, )).fetchone()
                    if exist:
                        print(f'Attention: {result} already used.')
                        user_input(field=field, password=password)
                    else:
                        return result
                elif (field == 'email' and is_valid_email(result)):
                    db = get_db()
                    exist = db.execute("SELECT u.email FROM users u WHERE u.email = %s;", (result, )).fetchone()
                    if exist:
                        print(f'Attention: {result} already used.')
                        user_input(field=field, password=password)
                    else:
                        return result
                




@click.command('create-admin')
def create_admin_user():
    username = user_input('username')
    email = user_input('email')
    print('Password has to contain:\n\
            At least 12 characters in length.\n\
            Contains at least one uppercase letter.\n\
            Contains at least one lowercase letter.\n\
            Contains at least one digit (number).\n\
            Contains at least one special character (e.g., !, @, #, $, %, etc.)')
    password = user_input('password', password=True)
    confirm_password = user_input('confirm password', password=True)
    if password != confirm_password:
            raise ValueError('Password not conform.')
    else:
        db = get_db()
        hashed_password = generate_password_hash(password=password)
        db.execute('insert into users(username, email, password, role_id) values(%s, %s, %s, %s);', (username, email, hashed_password, 1))
        print(f'User {username} create successfully')


       


def init_app(app):
    #app.teardown_appcontext() tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)

    #app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_user)