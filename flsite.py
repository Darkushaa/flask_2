# from flask import Flask, render_template, url_for, request, flash, session, redirect
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
#
# menu = [{"name": "Установка", "url": "install-flask"},
#         {"name": "Первое приложение", "url": "first-app"},
#         {"name": "Обратная связь", "url": "contact"}]
#
#
# @app.route("/")
# def index():
#     print(url_for('index'))
#     return render_template('index.html', menu=menu)
#
#
# @app.route("/about")
# def about():
#     print(url_for('about'))
#     return render_template('about.html', title="О сайте", menu=menu)
#
#
# @app.route("/contact", methods=["POST", "GET"])
# def contact():
#     if request.method == 'POST':
#         if len(request.form['username']) > 2:
#             flash('Сообщение отправлено', category='success')
#         else:
#             flash('Ошибка отправки', category='error')
#
#     return render_template('contact.html', title="О сайте", menu=menu)
#
#
# @app.route("/profile/<username>")
# def profile(username):
#     return f"Профиль пользователя: {username}"
#
#
# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if 'userLoggen' in session:
#         return redirect(url_for('profile', username=session['userLoggen']))
#     elif request.method == 'POST' and request.form['username'] == "selfedu" and request.form['psw'] == "123":
#         session['userLoggen'] = request.form['username']
#         return redirect(url_for('profile', username=session['userLoggen']))
#
#     return render_template('login.html', title="Авторозация", menu=menu)
#
#
# @app.errorhandler(404)
# def pagenotfound(error):
#     return render_template('page404.html', title="Страница не найдена", menu=menu)
#
#
# if __name__ == "__main__":
#     app.run(debug=True)
import sqlite3
import os
from flask import Flask, render_template, request, g

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'asdfkjklxzhckoiuyqwe'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'lin_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route("/")
def index():
    db = get_db()
    return render_template('index.html', menu=[])


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


if __name__ == "__main__":
    app.run(debug=True)
