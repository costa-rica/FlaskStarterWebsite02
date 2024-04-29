# Flask Starter Website 02

![Flask and DashAndData Logo](https://venturer.dashanddata.com/website_assets_images/dd_and_flask_02-400x209.png)

## Description
This is the framework for the typical website I use.

Major difference from FlaskStarterWebsite01
using SQLite instead of MySQL


## Documentation
This uses SQLite and there are many changes that need to be made. Some are:

### Build db in __init__.py

### SQLite password encryption
@bp_users.route '/login':
SQLite stores the passwords as bytes. When reading the password into the bcrypt.checkpw there is no need to encode the exisiting database password. Only the one being checked.
