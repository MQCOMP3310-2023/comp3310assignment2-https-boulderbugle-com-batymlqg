from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Restaurant, MenuItem
from sqlalchemy import asc
import speech_recognition as sr
from . import db
import requests
import logging
import os
import wave

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
            'cx': 1234,
            'key': 1234,
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
    print("query is:")
    print(query)
    if query:
        items = db.session.query(MenuItem).filter(MenuItem.name.ilike(f'%{query}%')).all()
        print(items)
        restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
        print(restaurant)
        return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
    else:
        return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))

@main.route('/search/', methods=['GET', 'POST'])
def search_restaurant():
    query = request.args.get('q', '')
    print("Query:", query)  # Print the query for debugging purposes
    if query:
        restaurant = db.session.query(Restaurant).filter(Restaurant.name.ilike(f'%{query}%')).first()
        if restaurant:
            restaurant_id = restaurant.id
            print(restaurant_id)
            items = db.session.query(MenuItem).filter(MenuItem.name.ilike(f'%{restaurant_id}%')).all()
            print(items)
            return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
    flash('Please enter a valid search query')
    return redirect(url_for('main.showRestaurants'))


# import wave

# @main.route("/speech", methods=["GET", "POST"])
# def speech():
#     file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voicetest', 'abcdefg.wav')
#     audio_data, sample_width, num_channels, frame_rate = read_wav_file(file_path)

#     print("Sample width:", sample_width)
#     print("Number of channels:", num_channels)
#     print("Frame rate:", frame_rate)

#     return "Speech processing completed"

# def read_wav_file(file_path):
#     with wave.open(file_path, 'rb') as wav_file:
#         sample_width = wav_file.getsampwidth()
#         num_channels = wav_file.getnchannels()
#         frame_rate = wav_file.getframerate()
#         num_frames = wav_file.getnframes()

#         audio_data = wav_file.readframes(num_frames)

#     return audio_data, sample_width, num_channels, frame_rate

# import os
# import wave
# from google.cloud import speech
# from google.cloud.speech_v1p1beta1.services.speech import SpeechClient


# os.environ["GOOGLE_API_KEY"] = "AIzaSyAPi9x5nSSVnCED8Khehgt3dBA5uDjmD8Q"

# @main.route("/speech", methods=["GET", "POST"])
# def speech():
#     file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voicetest', 'abcdefg.wav')
#     audio_data, sample_width, num_channels, frame_rate = read_wav_file(file_path)

#     print("Sample width:", sample_width)
#     print("Number of channels:", num_channels)
#     print("Frame rate:", frame_rate)

#     transcribed_text = transcribe_audio(audio_data, sample_width, frame_rate)

#     print("Transcribed text:", transcribed_text)

#     return "Speech processing completed"

# def read_wav_file(file_path):
#     with wave.open(file_path, 'rb') as wav_file:
#         sample_width = wav_file.getsampwidth()
#         num_channels = wav_file.getnchannels()
#         frame_rate = wav_file.getframerate()
#         num_frames = wav_file.getnframes()

#         audio_data = wav_file.readframes(num_frames)

#     return audio_data, sample_width, num_channels, frame_rate

# def transcribe_audio(audio_data, sample_width, frame_rate):
#     client = speech.SpeechClient()

#     config = {
#         "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         "sample_rate_hertz": frame_rate,
#         "language_code": "en-US",
#     }

#     audio = {"content": audio_data}

#     response = client.recognize(config=config, audio=audio)

#     transcribed_text = ""
#     for result in response.results:
#         transcribed_text += result.alternatives[0].transcript

#     return transcribed_text

import os
import wave
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types
from google.oauth2 import service_account

# Set the path to your JSON credentials file
credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google_search_keys', 'food-api-386807-89a88d306a8d.json')

# Create a credentials object from the JSON file
credentials = service_account.Credentials.from_service_account_file(credentials_path)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

@main.route("/speech", methods=["GET", "POST"])
def speech():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voicetest', 'UrbanBurgerAI.wav')
    audio_data, sample_width, num_channels, frame_rate = read_wav_file(file_path)

    print("Sample width:", sample_width)
    print("Number of channels:", num_channels)
    print("Frame rate:", frame_rate)

    transcribed_text = transcribe_audio(audio_data, sample_width, frame_rate)

    print("Transcribed text:", transcribed_text)

    return "Speech processing completed"

def read_wav_file(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        sample_width = wav_file.getsampwidth()
        num_channels = wav_file.getnchannels()
        frame_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()

        audio_data = wav_file.readframes(num_frames)

    return audio_data, sample_width, num_channels, frame_rate

from google.cloud import speech_v1p1beta1

def transcribe_audio(audio_data, sample_width, frame_rate):
    client = speech_v1p1beta1.SpeechClient(credentials=credentials)

    config = {
        "encoding": enums.RecognitionConfig.AudioEncoding.LINEAR16,
        "sample_rate_hertz": frame_rate,
        "language_code": "en-US",
    }

    audio = {"content": audio_data}

    response = client.recognize(config=config, audio=audio)

    print("Response:", response)  # Debug print for response object

    transcribed_text = ""
    for result in response.results:
        if result.alternatives:
            transcribed_text += result.alternatives[0].transcript

    print("Transcribed text:", transcribed_text)

    return transcribed_text


# def index():
#     transcript = ""
#     if request.method == "POST":
#         print("FORM DATA RECEIVED")

#         if "file" not in request.files:
#             return redirect(request.url)

#         file = request.files["file"]
#         if file.filename == "":
#             return redirect(request.url)

#         if file:
#             recognizer = sr.Recognizer()
#             audioFile = sr.AudioFile(file)
#             with audioFile as source:
#                 data = recognizer.record(source)
#             transcript = recognizer.recognize_google(data, key=None)

#         if query:
#             restaurant = db.session.query(Restaurant).filter(Restaurant.name.ilike(f'%{query}%')).first()
#             if restaurant:
#                 restaurant_id = restaurant.id
#                 print(restaurant_id)
#                 items = db.session.query(MenuItem).filter(MenuItem.name.ilike(f'%{restaurant_id}%')).all()
#                 print(items)
#                 return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
#     flash('Bro you fucked up')
#     return render_template('main.showRestraunts', transcript=transcript)
