from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask import Flask
from config import config
bootstrap = Bootstrap() # 使用tiwtter 框架
moment = Moment() # 管理時間渲染
mail = Mail() # send email function
db = SQLAlchemy() # db 對像是 SQLAlchemy 類的實例

def create_app(config_name): # config_name 是指要用哪種型態的app 紀錄在config裡面 {development, testing, production, default}
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app