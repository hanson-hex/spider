# /usr/bin/env python
#-*- coding:utf-8 -*-

from app import db


class ModelMixin(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = {1}'.format(k, v) for k, v in self.__dict__.items())
        return '<{0}: \n  {1}\n>'.format(class_name, '\n  '.join(properties))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class House(db.Model, ModelMixin):
    """
    拍卖房产数据
    """
    __tablename__ = 'house'
    # 编号
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 省份
    province = db.Column(db.String(100))
    # 城市
    city = db.Column(db.String(100))
    # 标的
    target = db.Column(db.String(500))
    # 现价
    currentPrice = db.Column(db.String(100))
    # 报名人数
    bidCount = db.Column(db.Integer)
    # 市场价
    marketPrice = db.Column(db.String(100))
    # 申请人数
    applyCount = db.Column(db.Integer)
    # 观看人数
    viewerNum = db.Column(db.Integer)
    # 开始时间
    startTime = db.Column(db.Integer)
    # 停止时间
    stopTime = db.Column(db.Integer)
    # 状态
    status = db.Column(db.String(100))
    # 处置单位
    department = db.Column(db.String(500))
    # 加价幅度
    addPrice = db.Column(db.String(100))
    # 保证金
    deposit = db.Column(db.String(100))
    # 起拍价
    startPrice = db.Column(db.String(100))
    # 竞拍周期
    period = db.Column(db.String(100))

    def __init__(self, form):
        self.province = form.get('province', '')
        self.city = form.get('city', '')
        self.target = form.get('target', '')
        self.currentPrice = int(form.get('currentPrice', -1))
        self.bidCount = int(form.get('bidCount', 0))
        self.marketPrice = int(form.get('marketPrice', -1))
        self.applyCount = int(form.get('applyCount', 0))
        self.viewerNum = int(form.get('viewerNum', 0))
        self.startTime = int(form.get('startTime', -1))
        self.stopTime = int(form.get('stopTime', -1))
        self.status = form.get('status', '')
        self.department = form.get('department', '')
        self.addPrice = form.get('addPrice', -1)
        self.deposit = form.get('deposit', '')
        self.period = form.get('period', '')
        self.startPrice = form.get('startPrice', -1)

    def json(self):
        d = dict(
            id=self.id,
            province=self.province,
            city=self.city,
            currentPrice=self.currentPrice,
            target=self.target,
            bidCount=self.bidCount,
            viewerNum=self.viewerNum,
            startTime=self.startTime,
            stopTime=self.stopTime,
            status=self.status,
            department=self.department,
            addPrice=self.addPrice,
            deposit=self.deposit,
            period=self.period,
            startPrice=self.startPrice
        )
        return d
