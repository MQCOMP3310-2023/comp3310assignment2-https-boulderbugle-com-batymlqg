
```
_________________________________________
/ IMPORTANT PLEASE READ                    \
|                                         |
|   ***********************************   |
|  *                                   *  |
|  *             IMPORTANT             *  |
|  *            PLEASE READ            *  |
|  *                                   *  |
|   ***********************************   |
|                                         |
|  ***********************************    |
| *                                   *   |
| * THIS CODEBASE REQUIRES AN API KEY *   |
| * FOR GOOGLE CLOUD PLATFORM (GCP)   *   |
| * TO FUNCTION PROPERLY.            *   |
| *                                 *   |
| * WITHOUT THE API KEY, THE CODE    *   |
| * WILL NOT WORK AS EXPECTED.      *    |
| ***********************************    |
|                                         |
| If you would like to obtain the API key, |
| please contact me at                    |
| jee.ong@students.mq.edu.au.              |
\_________________________________________/
          \
           \
             ^__^
             (oo)\_______
             (__)\       )\/\
                 ||----w |
                 ||     ||
```

# COMP3310 Assignment2
This is the code for Assignment2 for COMP3310 S1 2023.

This codebase implements a basic restaurant listing web application using Python and the Flask framework. Your task will be to modify the basic site to add new features focusing on secure application development principles.

# Setup

To setup the basic website you will need to have the following installed:

- python3
- pip

Pip is the package manager for Python.  You can install the remaining packages required for this task using pip. You will need to run the following:

- pip install flask flask-sqlalchemy flask-login

You should have at least the following versions installed: 
- Python             3.9.6
- Flask              2.2.3
- Flask-Login        0.6.2
- Flask-SQLAlchemy   3.0.3

You will also need sqlite installed for the database backend.

# Initialising the database

You should first initialise the database as follows:
- python initialise_db.py

This should create an sqlite database under the instance directory. You can view the contents of the database using the sqlite command line interface as follows:

sqlite3 instance/db.sqlite
> .schema  

CREATE TABLE restaurant (
	id INTEGER NOT NULL, 
	name VARCHAR(250) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE menu_item (
	name VARCHAR(80) NOT NULL, 
	id INTEGER NOT NULL, 
	description VARCHAR(250), 
	price VARCHAR(8), 
	course VARCHAR(250), 
	restaurant_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(restaurant_id) REFERENCES restaurant (id)
);
> select * from restaurant;
1|Urban Burger
2|Super Stir Fry
3|Panda Garden
4|Thyme for That Vegetarian Cuisine 
5|Tony's Bistro 
6|Andala's
7|Auntie Ann's Diner 
8|Cocina Y Amor 

The schema will be displayed, showing the structure of the restaurant and menu_item tables. You can also run a SELECT query to see the prepopulated restaurants and menu items.

Please note that the provided code does not mention adding a user in the schema. If you need to add user functionality to the application, you will need to modify the schema and the code accordingly.

You can see that the database comes prepopulated with some restaurants and some menu items. This is done in the initialise_db.py file.

# Run the website

You can run the website by typing:

- python run.py

You can now browse to the url http://localhost:8000/ to view the website.
