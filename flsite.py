# Lesson 11
import datetime

# from flask import Flask, render_template, make_response, redirect, url_for
#
# app = Flask(__name__)
#
# menu = [{"title": "Главная", "url": "/add_post"}]
#
#
# @app.route("/")
# def index():
#     return "<h1>Main Page</h1>", 200, {'Content-Type': 'text/plain'}
#
#
# @app.errorhandler(404)
# def pageNot(error):
#     return ("Страница не найдена", 404)
#
#
# @app.route('/transfer')
# def transfer():
#     return redirect(url_for('index'), 301)
#
#
# @app.before_first_request
# def before_first_request():
#     print("before_first_request() called")
#
#
# @app.after_request
# def after_request(response):
#     print("after_request() called")
#     return response
#
#
# @app.teardown_appcontext
# def teardown_request(response):
#     print("teardown_request() called")
#     return response
#
#
# if __name__ == "__main__":
#     app.run(debug=True)

# Lesson 12

# from flask import Flask, render_template, make_response, url_for, request
#
# app = Flask(__name__)
#
# menu = [{"title": "Главная", "url": "/"},
#         {"title": "Добавить статью", "url": "/add_post"}]
#
#
# @app.route("/")
# def index():
#     return "<h1>Main Page</h1>"
#
#
# @app.route("/login")
# def login():
#     log = ""
#     if request.cookies.get('logged'):
#         log = request.cookies.get('logged')
#
#     res = make_response(f"<h1>Форма авторизации</h1><p>logged: {log}")
#     res.set_cookie("logged", "yes")
#
#     return res
#
#
# @app.route("/logout")
# def logout():
#     res = make_response("<p>Вы больше не авторизовны!</p>")
#     res.set_cookie("logged", "", 0)
#     return res
#
#
# if __name__ == "__main__":
#     app.run(debug=True)

# Lesson 13

# from flask import Flask, render_template, make_response, url_for, request, session
# import datetime
# app = Flask(__name__)
# app.config['SECRET_KEY'] = '48293e0252f5aa9843b2017623c1d7c2e5b8f5ea'
# app.permanent_session_lifetime = datetime.timedelta(days=10)
#
#
# @app.route("/")
# def index():
#     if 'visits' in session:
#         session['visits'] = session.get('visits') + 1  # обновление данных сессии
#     else:
#         session['visits'] = 1  # запись данных в сессию
#     return f"<h1>Main Page</h1><p>Число просмотров: {session['visits']}"
#
#
# data = [1, 2, 3, 4]
#
#
# @app.route("/session")
# def session_data():
#     session.permanent = False
#     if 'data' not in session:
#         session['data'] = data
#     else:
#         session['data'][1] += 1
#         session.modified = True
#
#     return f"<p>session['data']: {session['data']}"
#
#
# if __name__ == "__main__":
#     app.run(debug=True)


import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = '48293e0252f5aa9843b2017623c1d7c2e5b8f5ee'

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
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединение с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    # '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route("/view")
def view():
    return render_template('framework-flask-intro.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route("/login")
def login():
    return render_template('login.html', menu=dbase.getMenu(), title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД ", "error")
        else:
            flash("Наверно заполнены поля ", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")


if __name__ == "__main__":
    app.run(debug=True)
