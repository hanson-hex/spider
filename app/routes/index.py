# /usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint
import json
from app.models.house import House

main = Blueprint('house', __name__)


@main.route('/')
def get_all():
    house_list = House.query.all()
    print(house_list)
    houses = [h.json() for h in house_list]
    return json.dumps(houses, indent=2, ensure_ascii=False)

