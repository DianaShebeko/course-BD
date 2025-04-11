import psycopg
from app import login_manager
from flask_login import UserMixin
from app import app

class User(UserMixin):
    def __init__(self, login, name, phone, password):
        self.login = login
        self.name = name
        self.phone = phone
        self.password = password

    def get_id(self):
        return self.login

@login_manager.user_loader
def load_user(login):
    with psycopg.connect(
        host=app.config['DB_SERVER'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        dbname=app.config['DB_NAME']
    ) as con:
        cur = con.cursor()
        login, name, phone, password = cur.execute('SELECT Login, Name, Phone, Password '
                    'FROM AppUser '
                    'WHERE Login = %s', (login,)).fetchone()

    return User(login, name, phone, password)