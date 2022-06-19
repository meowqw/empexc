from flask import Flask, render_template, request, redirect, make_response, session, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user
import os
import config

app = Flask(__name__)
login_manager = LoginManager(app)


# Подключение к БД
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.db}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app_root = os.path.dirname(os.path.abspath(__file__))


# Класс авторизации
class UserLogin():
    def fromDataBase(self, self_id, db):
        self.__user = db.query.filter_by(login=self_id).first()
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.__user


# Модель ДБ резюме
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(200), nullable=False)
    mname = db.Column(db.String(200), nullable=False)
    lname = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    profession = db.Column(db.String(200), nullable=False)
    skills = db.Column(db.String(1000), nullable=False)
    phone = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    info = db.Column(db.Text(), nullable=False)


# Модель ДБ пользователи
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)


# список профессий
professions = {"it": "IT",
               "auto": "Автобизнес",
               "managment": "Менеджмент",
               "jurisprudence": "Юриспруденция",
               "tourism": "Туризм",
               "sales": "Продажи",
               "design": "Дизайн",
               "security": "Безопасность",
               "insurance": "Страхование",
               "personnel": "Рабочий персонал",
               "consulting": "Консультирование"}


# сбор данных в словарь
def resume_data_to_dict(i):
    data = {'id': i.id,
            'fname': i.fname,
            'mname': i.mname,
            'lname': i.lname,
            'city': i.city,
            'data': i.date,
            'profession': i.profession,
            'skills': i.skills,
            'phone': i.phone,
            'email': i.email,
            'info': i.info}
    return data

# РОУТИНГ

# получить статус атризации
def check_auth():
    try:
        user = current_user.get_id().login
    except Exception as e:
        user = None
    return user

# получить статус авторизации (запрос)
@app.route('/check_auth')
def check():
    if check_auth() == None:
        return {'status': 'None'}
    else:
        return {'status': check_auth()}


# АВТОРИЗАЦИЯ
@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDataBase(user_id, Users)


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Авторизация"""
    if request.method == "POST":
        user_data = Users.query.filter_by(login=request.form['login']).first()
        if user_data.password == request.form['password'] and user_data.login == request.form['login']:
            user_login = UserLogin().create(str(user_data.login))
            login_user(user_login)
            print(True)
            return redirect(url_for('index'))
        else:
            print(False)
            return redirect(url_for('login'))

        # flash('Ошибка')
    return render_template('login.html')



@app.route('/')
def index():
    """Страница index"""

    return render_template('index.html', professions=professions, auth=check_auth())


@app.route('/resume_load')
def resume_load():
    """Прогрузка контента (резюме)"""

    resume = Resume.query.all()
    data = []
    for i in resume:
        data.append(resume_data_to_dict(i))
    return jsonify(data)


@app.route('/resume_add', methods=['POST', 'GET'])
def resume_add():
    """Добавление резюме"""
    content = request.get_json(silent=True)

    data = Resume(id=None,
                  fname=content['fname'],
                  mname=content['mname'],
                  lname=content['lname'],
                  city=content['city'],
                  date=content['date'],
                  profession=content['profession'],
                  skills=content['skills'],
                  phone=content['phone'],
                  email=content['email'],
                  info=content['info'])
    db.session.add(data)
    db.session.commit()
    return content


@app.route('/resume/<string:id>')
def resume(id):
    """Получение резюме по id"""
    resume = Resume.query.filter_by(id=id).first()

    data = {
        'id': resume.id,
        'fname': resume.fname,
        'mname': resume.mname,
        'lname': resume.lname,
        'city': resume.city,
        'date': str(resume.date).split(' ')[0],
        'profession': resume.profession,
        'skills': resume.skills,
        'phone': resume.phone,
        'email': resume.email,
        'info': resume.info}

    return jsonify(data)


@app.route('/resume_profession/<string:profession>')
def resume_profession(profession):
    """Получение резюме по profession"""
    resume = Resume.query.filter_by(profession=professions[profession]).all()

    data = []
    for i in resume:
        data.append(resume_data_to_dict(i))

    return jsonify(data)


@app.route('/resume_del/<string:id>')
def resume_del(id):
    """Удаление резюме"""
    Resume.query.filter_by(id=id).delete()
    db.session.commit()
    return id


@app.route('/search/<string:text>')
def resume_search(text):
    """Получить резюме поиск"""

    resume = Resume.query.all()
    if len(text) != 0:

        data = []
        for i in resume:
            if text.lower() in f'{i.fname} {i.mname} {i.lname} {i.city} \
            {i.date} {i.profession} {i.skills} {i.phone} {i.email} {i.info}'.lower():
                data.append(resume_data_to_dict(i))
    else:
        for i in resume:
            data.append(resume_data_to_dict(i))

    return jsonify(data)


if __name__ == '__main__':
    # создание таблиц БД
    db.create_all()
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True, port=5005)
