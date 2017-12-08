# /usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config.from_pyfile('app.conf')

db = SQLAlchemy(app)

# 引入蓝图
from app.routes.index import main as route_house

"""
在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
蓝图可以拥有自己的静态资源路径、模板路径
用法如下
"""
# 注册蓝图
# 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀
app.register_blueprint(route_house, url_prefix='/house')


