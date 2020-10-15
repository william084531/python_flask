from flask import Flask, render_template, session,  url_for, flash
from flask import request
# from flask import make_response
from flask import redirect
from flask import abort
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread

def make_shell_context():
 return dict(app=app, db=db, User=User, Role=Role)


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__) # 以檔案名稱建立app
app.config['SECRET_KEY'] = 'hard to guess string' # 設置密鑰
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
manager = Manager(app)
manager.add_command("shell", Shell(make_context=make_shell_context))
bootstrap = Bootstrap(app) # 使用tiwtter 框架
moment = Moment(app) # 管理時間渲染
db = SQLAlchemy(app) # db 對像是 SQLAlchemy 類的實例
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))
mail = Mail(app)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
def send_email(to, subject, template, **kwargs):
     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
     sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
     msg.body = render_template(template + '.txt', **kwargs)
     # msg.html = render_template(template + '.html', **kwargs)
     thr = Thread(target=send_async_email, args=[app, msg])
     thr.start()
     return thr


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique = True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
class NameForm(Form):
   name = StringField('What is your name?', validators=[Required()])
   submit = SubmitField('Submit')

def load_user(id):
    user = {'1':'william', '2':'Maia', '3':'Work'}
    if not user.get(id):
        return None
    else:
        return user.get(id)

# 建立網站首頁回應方式
@app.route("/", methods=['GET', 'POST']) # / 表示網站首頁
def home(): # 回應首頁連線的函式
    # user_agent = request.headers.get('User-Agent')
    # return '<p> Your browser is %s</p>' % user_agent # 回傳首頁內容
    # return '<h1>Bad Request</h1>', 400
    # response = make_response('<h1>This Web contain cookies!</h1>')
    # response.set_cookie('answer', '42')
    # return response
    # return redirect('http://www.example.com')
    db.create_all() # 先頭創建表單，如果沒有這行就無法建立表單，會有operational error
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_users', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('home'))
    return render_template('home.html', form=form, name=session.get('name'), known=session.get('known', False), current_time=datetime.utcnow())

# 添加了一個動態路由。訪問這個地址時，你會看到一則針
# 對個人的歡迎消息。
@app.route('/users/<name>')
def user(name):
    # return '<h1>Welcome %s!<h1>'% name
    return render_template('user.html', name=name)
@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        return render_template('404.html'), 404
    else:
        return render_template('user.html', name=user)

@app.errorhandler(404)
def pag_not_find(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def pag_not_find(e):
    return render_template('500.html'), 500
# 啟動網站伺服器
if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()
