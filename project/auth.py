from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user
from sqlalchemy import text
from .models import User
from . import db, app
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')