from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Restaurant, MenuItem
from sqlalchemy import asc
from . import db
import requests
import logging
import os

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/restaurant/')
def showRestaurants():
  restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
  return render_template('restaurants.html', restaurants = restaurants)

#Create a new restaurant
@main.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
  if request.method == 'POST':
      newRestaurant = Restaurant(name = request.form['name'])
      db.session.add(newRestaurant)
      flash('New Restaurant %s Successfully Created' % newRestaurant.name)
      db.session.commit()
      return redirect(url_for('main.showRestaurants'))
  else:
      return render_template('newRestaurant.html')

#Edit a restaurant
@main.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
  editedRestaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
  if request.method == 'POST':
      if request.form['name']:
        editedRestaurant.name = request.form['name']
        flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
        return redirect(url_for('main.showRestaurants'))
  else:
    return render_template('editRestaurant.html', restaurant = editedRestaurant)


#Delete a restaurant
@main.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
  restaurantToDelete = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
  if request.method == 'POST':
    db.session.delete(restaurantToDelete)
    flash('%s Successfully Deleted' % restaurantToDelete.name)
    db.session.commit()
    return redirect(url_for('main.showRestaurants', restaurant_id = restaurant_id))
  else:
    return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)

#Show a restaurant menu
# @main.route('/restaurant/<int:restaurant_id>/')
# @main.route('/restaurant/<int:restaurant_id>/menu/')
# def showMenu(restaurant_id):
#     restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
#     items = db.session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
#     for item in items:
#        print(item.description)
#     return render_template('menu.html', items = items, restaurant = restaurant)

@main.route('/restaurant/<int:restaurant_id>/')
@main.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = db.session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    image_urls = {}
    
    api_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google_search_keys', 'api_key.txt')
    with open(api_key_file, 'r') as f:
        api_key = f.read().strip()

    cx_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google_search_keys', 'eng_id.txt')
    with open(cx_file, 'r') as f:
        cx_key = f.read().strip()

    for item in items:
        search_url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': item.name,
            'num': 1,
            'searchType': 'image',
            'cx': cx_key,
            'key': api_key,
        }

        response = requests.get(search_url, params=params)
        response_json = response.json()
        print(response)

        if 'items' in response_json and len(response_json['items']) > 0:
            image_url = response_json['items'][0]['link']
            image_urls[item.id] = image_url
            print("Got an image")
            print(image_url)
        else:
            print(f"No image found for item {item.name}")

    if not image_urls:
        print("No images found for any items")

    return render_template('menu.html', items=items, restaurant=restaurant, image_urls=image_urls)

     
#Create a new menu item
@main.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
  restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
  if request.method == 'POST':
      newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
      db.session.add(newItem)
      db.session.commit()
      flash('New Menu %s Item Successfully Created' % (newItem.name))
      return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
  else:
      return render_template('newmenuitem.html', restaurant_id = restaurant_id)

#Edit a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):

    editedItem = db.session.query(MenuItem).filter_by(id = menu_id).one()
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        db.session.add(editedItem)
        db.session.commit() 
        flash('Menu Item Successfully Edited')
        return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)


#Delete a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    itemToDelete = db.session.query(MenuItem).filter_by(id = menu_id).one() 
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item = itemToDelete)

@main.route('/search/<int:restaurant_id>', methods=['GET', 'POST'])
def search_menu_items(restaurant_id):
    print("hello")
    query = request.args.get('q', '')
    if query:
        items = db.session.query(MenuItem).filter(MenuItem.name.ilike(f'%{query}%')).all()
        restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('search_results.html', items=items, restaurant=restaurant, query=query)
    else:
        flash('Please enter a search query')
        return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))



