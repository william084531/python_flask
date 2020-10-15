from . import main
from .. import db
from .forms import NameForm
from ..email import send_email
from ..models import Role, User
from flask import render_template, session, redirect, url_for
from datetime import datetime
from flask import current_app

@main.route("/", methods=['GET', 'POST']) # / 表示網站首頁
def home(): # 回應首頁連線的函式
    db.create_all() # 先頭創建表單，如果沒有這行就無法建立表單，會有operational error
    form = NameForm()
    app_config = current_app.config
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app_config['FLASKY_ADMIN']:
                send_email(app_config['FLASKY_ADMIN'], 'New User', 'mail/new_users', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.home'))
    return render_template('home.html', form=form, name=session.get('name'), known=session.get('known', False), current_time=datetime.utcnow())