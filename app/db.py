import os
import dotenv

import psycopg
from psycopg.rows import dict_row

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


def init_app(app):
    #app.teardown_appcontext() tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)

    #app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)