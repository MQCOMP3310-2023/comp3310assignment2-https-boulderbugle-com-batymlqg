from flask import Blueprint, jsonify
from .models import Restaurant, MenuItem
from sqlalchemy import text
from . import db
import json as pyjs

json = Blueprint('json', __name__)

#JSON APIs to view Restaurant Information
#SQL query built from user-controlled sources - fixed
@json.route('/restaurant/<restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    s = text('select * from menu_item where restaurant_id = :restaurant_id ')
    items = db.session.execute(s, {'restaurant_id': restaurant_id}).fetchall()
    items_list = [dict(row) for row in items]
    return pyjs.dumps(items_list)

# SQL query built from user-controlled sources - fixed
@json.route('/restaurant/<restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    s = text('SELECT * FROM menu_item WHERE id = :menu_id LIMIT 1')
    items = db.session.execute(s, {'menu_id': menu_id}).fetchone()
    if items is not None:
        items_list = [dict(items)]
    else:
        items_list = []
        
    return pyjs.dumps(items_list)

@json.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = db.session.execute(text('select * from restaurant'))
    rest_list = [ r._asdict() for r in restaurants ]
    return pyjs.dumps(rest_list)




