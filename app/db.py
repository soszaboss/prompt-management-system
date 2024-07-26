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
    """
    Regex pattern that checks if a password meets the following requirements:
    - At least 12 characters in length.
    - Contains at least one uppercase letter.
    - Contains at least one lowercase letter.
    - Contains at least one digit (number).
    - Contains at least one special character (e.g., !, @, #, $, %, etc.).
    """
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&*])[A-Za-z\d@#$%^&*]{12,}$"
    return bool(re.match(pattern, password))

def user_input(field: str, password: bool = False) -> str:
    """
    Prompt the user for input and validate it.

    Args:
        field (str): The field name (e.g., 'username', 'email').
        password (bool): Whether the input is for a password.

    Returns:
        str: The validated user input.
    """
    while True:
        if password:
            result = getpass(prompt=f'{field}: ')
            if not result:
                print(f'{field} cannot be empty. Please try again.')
            else:
                return result
        else:
            result = input(f'{field}: ').strip()
            if not result:
                print(f'{field} cannot be empty. Please try again.')
            else:
                db = get_db()
                if field == 'username':
                    exist = db.execute("SELECT username FROM users WHERE username = %s;", (result,)).fetchone()
                    if exist:
                        print(f'Attention: {result} is already used. Please choose another username.')
                    else:
                        return result
                elif field == 'email':
                    if is_valid_email(result):
                        exist = db.execute("SELECT email FROM users WHERE email = %s;", (result,)).fetchone()
                        if exist:
                            print(f'Attention: {result} is already used. Please choose another email.')
                        else:
                            return result
                    else:
                        print('Invalid email format. Please try again.')

@click.command('createsuperuser')
def create_admin_user():
    username = user_input('username')
    email = user_input('email')
    print('Password must contain:\n\
            - At least 12 characters in length.\n\
            - At least one uppercase letter.\n\
            - At least one lowercase letter.\n\
            - At least one digit (number).\n\
            - At least one special character (e.g., !, @, #, $, %, etc.)')
    while True:
        password = user_input('password', password=True)
        if not validate_password(password):
            print('Password does not meet the criteria. Please try again.')
            continue
        confirm_password = user_input('confirm password', password=True)
        if password != confirm_password:
            print('Passwords do not match. Please try again.')
        else:
            break

    db = get_db()
    hashed_password = generate_password_hash(password)
    user = db.execute("insert into users(username, email, password, role_id, is_activated) values(%s, %s, %s, %s, %s);", (username, email, hashed_password, 1, 't'))
    print(f'User {username} account created successfully.')


       


def init_app(app):
    #app.teardown_appcontext() tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)

    #app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_user)