from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Restaurant, MenuItem
from sqlalchemy import asc
from . import db


main = Blueprint('main', __name__)

#Show the profile page
@main.route('/profile')
@login_required
#Since this route is decorated with @login_required decorator, we could access all of the current_user
#attributes. we set name=current_user.name to be able to generate the user's name to the profile page
def profile():
    return render_template('profile.html', name=current_user.name, role=current_user.role)

#Show all restaurants
@main.route('/')
@main.route('/restaurant/')
def showRestaurants():
  restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
  return render_template('restaurants.html', restaurants = restaurants)

#Create a new restaurant & assign that restaurannt to the restaurant owner 
@main.route('/restaurant/new/', methods=['GET','POST'])
@login_required
def newRestaurant():
  if request.method == 'POST':
      newRestaurant = Restaurant(name = request.form['name'], owner_id=current_user.id)
      db.session.add(newRestaurant)
      flash('New Restaurant %s Successfully Created' % newRestaurant.name)
      db.session.commit()
      return redirect(url_for('main.showRestaurants'))
  else:
      return render_template('newRestaurant.html')

#Edit a restaurant
@main.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
  editedRestaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
  
  #Check the access if it belongs to the owner of this restarant or it is the admin:
  if current_user.id != editedRestaurant.owner_id and current_user.role != 'admin':
    flash('You are not authorised to change the name of this restaurant')
    return redirect(url_for('main.showRestaurants'))
    
  if request.method == 'POST':
      if request.form['name']:
        editedRestaurant.name = request.form['name']
        db.session.commit()
        flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
        return redirect(url_for('main.showRestaurants'))
  else:
    return render_template('editRestaurant.html', restaurant = editedRestaurant)

#Delete a restaurant
@main.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
@login_required
def deleteRestaurant(restaurant_id):
  restaurantToDelete = db.session.query(Restaurant).filter_by(id = restaurant_id).one()

  #Check the access if it belongs to the owner of this restarant or it is the admin:
  if current_user.id != restaurantToDelete.owner_id and current_user.role != 'admin':
    flash('You are not authorised to delete this restaurant')
    return redirect(url_for('main.showRestaurants'))

  if request.method == 'POST':
    db.session.delete(restaurantToDelete)
    flash('%s Successfully Deleted' % restaurantToDelete.name)
    db.session.commit()
    return redirect(url_for('main.showRestaurants', restaurant_id = restaurant_id))
  else:
    return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)

#Show a restaurant menu
@main.route('/restaurant/<int:restaurant_id>/')
@main.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = db.session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html', items = items, restaurant = restaurant)
     
#Create a new menu item
@main.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
@login_required
def newMenuItem(restaurant_id):
  restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()

  #Check the access if it belongs to the owner of this restarant or it is the admin:
  if current_user.id != restaurant.owner_id and current_user.role != 'admin':
    flash('You are not authorised to create a new menu item for this restaurant')
    return redirect(url_for('main.showRestaurants'))
  
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
@login_required
def editMenuItem(restaurant_id, menu_id):

    editedItem = db.session.query(MenuItem).filter_by(id = menu_id).one()
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    
    #Check the access if it belongs to the owner of this restarant or it is the admin:
    if current_user.id != restaurant.owner_id and current_user.role != 'admin':
        flash('You are not authorised to edit a menu item for this restaurant')
        return redirect(url_for('main.showRestaurants'))

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
@login_required
def deleteMenuItem(restaurant_id,menu_id):
    restaurant = db.session.query(Restaurant).filter_by(id = restaurant_id).one()
    itemToDelete = db.session.query(MenuItem).filter_by(id = menu_id).one() 

    #Check the access if it belongs to the owner of this restarant or it is the admin:
    if current_user.id != restaurant.owner_id and current_user.role != 'admin':
        flash('You are not authorised to delete a menu item for this restaurant')
        return redirect(url_for('main.showRestaurants'))

    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('main.showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item = itemToDelete)
