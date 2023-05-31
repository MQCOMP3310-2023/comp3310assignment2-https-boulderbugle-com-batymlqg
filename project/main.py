from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask import request
from flask_login import login_required, current_user
from .models import Restaurant, MenuItem
from sqlalchemy import asc
import speech_recognition as sr
from . import db
import requests
import logging
import os
import wave
from google.cloud import speech_v1p1beta1
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types
from google.oauth2 import service_account
from nltk.corpus import wordnet
from sqlalchemy import or_
from collections import Counter
from flask import jsonify
import datetime
import json
from flask_cors import CORS
import sounddevice as sd
import soundfile as sf
import numpy as np


main = Blueprint("main", __name__)

credentials_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "google_search_keys",
    "food-api-386807-d60daa8e2a3f.json",
)

credentials = service_account.Credentials.from_service_account_file(credentials_path)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

@main.route("/delete_wav_files", methods=["POST"])
def delete_wav_files():
    directory = "./project/voicetest" 
    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)

    return "WAV files deleted successfully"

@main.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html", name=current_user.name, role=current_user.role
    )

@main.route("/record", methods=["POST"])
def record():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    sample_rate = 44100  
    duration = 5  

    audio = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1)
    sd.wait()  

    file_path = f"./project/voicetest/{timestamp}.wav"  
    sf.write(file_path, audio, sample_rate)

    return file_path


@main.route("/")
@main.route("/restaurant/")
def showRestaurants():
    restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
    show_search_bar = True
    return render_template(
        "restaurants.html", restaurants=restaurants, show_search_bar=show_search_bar
    )

@main.route("/restaurant/new/", methods=["GET", "POST"])
@login_required
def newRestaurant():
    if request.method == "POST":
        newRestaurant = Restaurant(name=request.form["name"], owner_id=current_user.id)
        db.session.add(newRestaurant)
        flash("New Restaurant %s Successfully Created" % newRestaurant.name)
        db.session.commit()
        return redirect(url_for("main.showRestaurants"))
    else:
        return render_template("newRestaurant.html")


@main.route("/restaurant/<int:restaurant_id>/edit/", methods=["GET", "POST"])
@login_required
def editRestaurant(restaurant_id):
    editedRestaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()

    if current_user.id != editedRestaurant.owner_id and current_user.role != "admin":
        flash("You are not authorised to change the name of this restaurant")
        return redirect(url_for("main.showRestaurants"))

    if request.method == "POST":
        if request.form["name"]:
            editedRestaurant.name = request.form["name"]
            db.session.commit()
            flash("Restaurant Successfully Edited %s" % editedRestaurant.name)
            return redirect(url_for("main.showRestaurants"))
    else:
        return render_template("editRestaurant.html", restaurant=editedRestaurant)


@main.route("/restaurant/<int:restaurant_id>/delete/", methods=["GET", "POST"])
@login_required
def deleteRestaurant(restaurant_id):
    restaurantToDelete = db.session.query(Restaurant).filter_by(id=restaurant_id).one()

    if current_user.id != restaurantToDelete.owner_id and current_user.role != "admin":
        flash("You are not authorised to delete this restaurant")
        return redirect(url_for("main.showRestaurants"))

    if request.method == "POST":
        db.session.delete(restaurantToDelete)
        flash("%s Successfully Deleted" % restaurantToDelete.name)
        db.session.commit()
        return redirect(url_for("main.showRestaurants", restaurant_id=restaurant_id))
    else:
        return render_template("deleteRestaurant.html", restaurant=restaurantToDelete)


@main.route("/restaurant/<int:restaurant_id>/")
@main.route("/restaurant/<int:restaurant_id>/menu/")
def showMenu(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = db.session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template("menu.html", items=items, restaurant=restaurant)


@main.route("/restaurant/<int:restaurant_id>/menu/new/", methods=["GET", "POST"])
@login_required
def newMenuItem(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()

    if current_user.id != restaurant.owner_id and current_user.role != "admin":
        flash("You are not authorised to create a new menu item for this restaurant")
        return redirect(url_for("main.showRestaurants"))

    if request.method == "POST":
        newItem = MenuItem(
            name=request.form["name"],
            description=request.form["description"],
            price=request.form["price"],
            course=request.form["course"],
            restaurant_id=restaurant_id,
        )
        db.session.add(newItem)
        db.session.commit()
        flash("New Menu %s Item Successfully Created" % (newItem.name))
        return redirect(url_for("main.showMenu", restaurant_id=restaurant_id))
    else:
        return render_template("newmenuitem.html", restaurant_id=restaurant_id)


@main.route(
    "/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit", methods=["GET", "POST"]
)
@login_required
def editMenuItem(restaurant_id, menu_id):
    editedItem = db.session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()

    if current_user.id != restaurant.owner_id and current_user.role != "admin":
        flash("You are not authorised to edit a menu item for this restaurant")
        return redirect(url_for("main.showRestaurants"))

    if request.method == "POST":
        if request.form["name"]:
            editedItem.name = request.form["name"]
        if request.form["description"]:
            editedItem.description = request.form["description"]
        if request.form["price"]:
            editedItem.price = request.form["price"]
        if request.form["course"]:
            editedItem.course = request.form["course"]
        db.session.add(editedItem)
        db.session.commit()
        flash("Menu Item Successfully Edited")
        return redirect(url_for("main.showMenu", restaurant_id=restaurant_id))
    else:
        return render_template(
            "editmenuitem.html",
            restaurant_id=restaurant_id,
            menu_id=menu_id,
            item=editedItem,
        )


@main.route(
    "/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete", methods=["GET", "POST"]
)
@login_required
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = db.session.query(MenuItem).filter_by(id=menu_id).one()

    if current_user.id != restaurant.owner_id and current_user.role != "admin":
        flash("You are not authorised to delete a menu item for this restaurant")
        return redirect(url_for("main.showRestaurants"))

    if request.method == "POST":
        db.session.delete(itemToDelete)
        db.session.commit()
        flash("Menu Item Successfully Deleted")
        return redirect(url_for("main.showMenu", restaurant_id=restaurant_id))
    else:
        return render_template("deleteMenuItem.html", item=itemToDelete)


@main.route("/search/<int:restaurant_id>", methods=["GET", "POST"])
def search_menu_items(restaurant_id):
    query = request.args.get("q", "")
    if query:
        items = (
            db.session.query(MenuItem).filter(MenuItem.name.ilike(f"%{query}%")).all()
        )
        restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
        return redirect(url_for("main.showMenu", restaurant_id=restaurant_id))
    else:
        return redirect(url_for("main.showMenu", restaurant_id=restaurant_id))


@main.route("/search/", methods=["GET", "POST"])
def search_restaurant():
    query = request.args.get("q", "")
    if query:
        word_list = create_word_list(query)

        conditions = [Restaurant.name.ilike(f"%{word}%") for word in word_list]
        conditions += [MenuItem.name.ilike(f"%{word}%") for word in word_list]
        conditions += [MenuItem.description.ilike(f"%{word}%") for word in word_list]
        query = db.session.query(Restaurant).filter(or_(*conditions))

        rows = query.all()

        restaurant_counter = Counter(row.name for row in rows)
        most_common = restaurant_counter.most_common()

        word_counter = Counter(word for row in rows for word in word_list)
        word_counts = word_counter.items()

        if rows:
            restaurant_id = rows[0].id
            restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
            items = (
                db.session.query(MenuItem)
                .filter(MenuItem.restaurant_id == restaurant_id)
                .all()
            )
            return render_template("menu.html", items=items, restaurant=restaurant)

    flash("Please enter a valid search query")
    return redirect(url_for("main.showRestaurants"))


def create_word_list(query):
    word_list = query.split()

    for i in range(len(word_list)):
        word = word_list[i].lower()

        synsets = wordnet.synsets(word)

        for synset in synsets:
            for synonym in synset.lemmas():
                similar_word = synonym.name().replace("_", " ")
                word_list.append(similar_word)

    word_list = list(set(word_list))
    return word_list


@main.route("/speech", methods=["GET", "POST"])
def speech():
    file_path = request.json.get("file_path")
    audio_data, sample_width, num_channels, frame_rate = read_wav_file(file_path)
    transcribed_text = transcribe_audio(audio_data, sample_width, frame_rate)
    word_list = create_word_list(transcribed_text)

    if transcribed_text:
        conditions = [Restaurant.name.ilike(f"%{word}%") for word in word_list]
        query = db.session.query(Restaurant).filter(or_(*conditions))

        restaurant = query.first()
        if restaurant:
            restaurant_id = restaurant.id
            items = (
                db.session.query(MenuItem)
                .filter(MenuItem.restaurant_id == restaurant_id)
                .all()
            )
            return url_for("main.showMenu", restaurant_id=restaurant_id)

    flash("Please enter a valid search query")
    return redirect(url_for("main.showRestaurants"))


def read_wav_file(file_path):
    with wave.open(file_path, "rb") as wav_file:
        sample_width = wav_file.getsampwidth()
        num_channels = wav_file.getnchannels()
        frame_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()

        audio_data = wav_file.readframes(num_frames)

    return audio_data, sample_width, num_channels, frame_rate


def transcribe_audio(audio_data, sample_width, frame_rate):
    client = speech_v1p1beta1.SpeechClient(credentials=credentials)
    print(credentials)

    config = {
        "encoding": enums.RecognitionConfig.AudioEncoding.LINEAR16,
        "sample_rate_hertz": frame_rate,
        "language_code": "en-US",
    }

    audio = {"content": audio_data}

    response = client.recognize(config=config, audio=audio)

    print("Response:", response)

    transcribed_text = ""
    for result in response.results:
        if result.alternatives:
            transcribed_text += result.alternatives[0].transcript

    print("Transcribed text:", transcribed_text)

    return transcribed_text


def create_word_list(transcribed_text):
    word_list = transcribed_text.split()

    for i in range(len(word_list)):
        word = word_list[i].lower()

        synsets = wordnet.synsets(word)

        for synset in synsets:
            for synonym in synset.lemmas():
                similar_word = synonym.name().replace("_", " ")
                word_list.append(similar_word)

    word_list = list(set(word_list))
    return word_list

