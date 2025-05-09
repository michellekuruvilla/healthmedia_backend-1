# imports from flask
import json
import os
from urllib.parse import urljoin, urlparse
from flask import abort, redirect, render_template, request, send_from_directory, url_for, jsonify  # import render_template from "public" flask libraries
from flask_login import current_user, login_user, logout_user
from flask.cli import AppGroup
from flask_login import current_user, login_required
from flask import current_app
from werkzeug.security import generate_password_hash
import shutil
from model.comment import initComments


# import "objects" from "this" project
from __init__ import app, db, login_manager  # Key Flask objects
# API endpoints
from api.comments import comment_api
from api.user import user_api
from api.pfp import pfp_api
from api.nestImg import nestImg_api # Justin added this, custom format for his website
from api.post import post_api
from api.channel import channel_api
from api.group import group_api
from api.section import section_api
from api.nestPost import nestPost_api # Justin added this, custom format for his website
from api.messages_api import messages_api # Adi added this, messages for his website
from api.vote import vote_api
from api.vacation import vacation_api
from api.student import student_api # Anyi added
from api.landscape import landscape_api
# from api.weatherstatic import weather_api
from api.explore import explore_api
from api.destinations import destinations_api #michelle
from api.weather import weather_api
from api.length import length_api




# database Initialization functions
from model.carChat import CarChat
from model.user import User, initUsers
from model.section import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.favorite import Favorite, initFavorite
from model.nestPost import NestPost, initNestPosts # Justin added this, custom format for his website
from model.vote import Vote, initVotes
from model.vacation import Vacation, initVacation
from model.landscape import Landscape, initLandscape
from model.explore import Explore, initExplore
from model.weather import Weather, initWeather
from model.length import Length, initLength
# server only Views




# register URIs for api endpoints
app.register_blueprint(comment_api)
app.register_blueprint(messages_api) # Adi added this, messages for his website
app.register_blueprint(user_api)
app.register_blueprint(pfp_api)
app.register_blueprint(post_api)
app.register_blueprint(channel_api)
app.register_blueprint(group_api)
app.register_blueprint(vacation_api)
app.register_blueprint(section_api)
app.register_blueprint(student_api)
app.register_blueprint(landscape_api)
app.register_blueprint(weather_api)
app.register_blueprint(explore_api)
app.register_blueprint(destinations_api)
# Added new files to create nestPosts, uses a different format than Mortensen and didn't want to touch his junk
app.register_blueprint(nestPost_api)
app.register_blueprint(nestImg_api)
app.register_blueprint(vote_api)
app.register_blueprint(length_api)




# Tell Flask-Login the view function name of your login route
login_manager.login_view = "login"




@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', next=request.path))




# register URIs for server pages
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




@app.context_processor
def inject_user():
    return dict(current_user=current_user)




# Helper function to check if the URL is safe for redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc




@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_page = request.args.get('next', '') or request.form.get('next', '')




    # Check if the request method is POST
    # print("Test point 4")
    if request.method == 'POST':
        # print("Test point 3")
        username = request.form.get('username')
        password = request.form.get('password')




        # Fetch the user from the database
        user = User.query.filter_by(_uid=username).first()




        # Validate the user's credentials
        # print("Test point 1")
        if user and user.is_password(password):
            # print("Test point 2")
            # Log the user in
            remember_me = 'remember_me' in request.form  # Checkbox in login form
            login_user(user, remember=remember_me)




            # Check if the next page URL is safe
            if not is_safe_url(next_page):
                return abort(400)




            # Redirect to the next page or the index
            return redirect(next_page or url_for('index'))
        else:
            error = 'Invalid username or password.'




    # Render the login page with the error (if any)
    return render_template("login.html", error=error, next=next_page)




@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    error = None




    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')




        # Check if the username already exists
        existing_user = User.query.filter_by(_uid=username).first()
        if existing_user:
            error = 'Username already exists. Please choose a different one.'
        else:
            # Hash the password before saving it
            hashed_password = generate_password_hash(password)




            # Create a new user object
            new_user = User(name=name, _uid=username, _password=hashed_password)


            # Add the user to the database
            db.session.add(new_user)
            db.session.commit()


            # Log the new user in
            login_user(new_user)


            # Redirect to the index or a welcome page
            return redirect(url_for('index'))


    # Render the sign-up page with any error messages
    return render_template("sign_up.html", error=error)




   
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))




@app.errorhandler(404)  # catch for URL not found
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404




@app.route('/')  # connects default URL to index() function
def index():
    print("Home:", current_user)
    return render_template("index.html")




@app.route('/users/table')
@login_required
def utable():
    users = User.query.all()
    return render_template("utable.html", user_data=users)




@app.route('/users/table2')
@login_required
def u2table():
    users = User.query.all()
    return render_template("u2table.html", user_data=users)

@app.route('/landscapes')
@login_required
def landscape():
    landscapes = Landscape.query.all()
    return render_template("landscape.html", landscapes=landscapes)


# Helper function to extract uploads for a user (ie PFP image)
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
 
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.delete()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'error': 'User not found'}), 404




@app.route('/users/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
   
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404




    # Set the new password
    if user.update({"password": app.config['DEFAULT_PASSWORD']}):
        return jsonify({'message': 'Password reset successfully'}), 200
    return jsonify({'error': 'Password reset failed'}), 500








# Create an AppGroup for custom commands
custom_cli = AppGroup('custom', help='Custom commands')




# Define a command to run the data generation functions
@custom_cli.command('generate_data')
def generate_data():
    initUsers()
    initSections()
    initGroups()
    initChannels()
    initPosts()
    initFavorite()
    initNestPosts()
    initVotes()
    initVacation()
    initComments()
    initLandscape()
    initExplore()
    initWeather()
    initLength()




# Backup the old database
def backup_database(db_uri, backup_uri):
    """Backup the current database."""
    if backup_uri:
        db_path = db_uri.replace('sqlite:///', 'instance/')
        backup_path = backup_uri.replace('sqlite:///', 'instance/')
        shutil.copyfile(db_path, backup_path)
        print(f"Database backed up to {backup_path}")
    else:
        print("Backup not supported for production database.")




# Extract data from the existing database
def extract_data():
    data = {}
    with app.app_context():
        data['users'] = [user.read() for user in User.query.all()]
        data['sections'] = [section.read() for section in Section.query.all()]
        data['groups'] = [group.read() for group in Group.query.all()]
        data['channels'] = [channel.read() for channel in Channel.query.all()]
        data['vacations'] = [vacation.read() for vacation in Vacation.query.all()]
        data['Lengths'] = [Length.read() for Length in Length.query.all()]
        data['posts'] = [post.read() for post in Post.query.all()]
        data['favorites'] = [favorite.read() for favorite in Favorite.query.all()]
        data['landscapes'] = [landscape.read() for landscape in Landscape.query.all()]
        data['explores'] = [explore.read() for explore in Explore.query.all()]
        data['weathers'] = [weather.read() for weather in Weather.query.all()]
    return data




# Save extracted data to JSON files
def save_data_to_json(data, directory='backup'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for table, records in data.items():
        with open(os.path.join(directory, f'{table}.json'), 'w') as f:
            json.dump(records, f)
    print(f"Data backed up to {directory} directory.")




# Load data from JSON files
def load_data_from_json(directory='backup'):
    data = {}
    for table in ['users', 'sections', 'groups', 'channels','posts', 'vacations','lengths']:
        with open(os.path.join(directory, f'{table}.json'), 'r') as f:
            data[table] = json.load(f)
    return data




# Restore data to the new database
def restore_data(data):
    with app.app_context():
        users = User.restore(data['users'])
        _ = Section.restore(data['sections'])
        _ = Group.restore(data['groups'], users)
        _ = Channel.restore(data['channels'])
        _ = Vacation.restore(data['vacations'])
        _ = Lengths.restore(data['lengths'])
        _ = Post.restore(data['posts'])
        _ = Favorite.restore(data['posts'])
        _ = Landscape.restore(data['posts'])
    print("Data restored to the new database.")




# Define a command to backup data
@custom_cli.command('backup_data')
def backup_data():
    data = extract_data()
    save_data_to_json(data)
    backup_database(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_BACKUP_URI'])




# Define a command to restore data
@custom_cli.command('restore_data')
def restore_data_command():
    data = load_data_from_json()
    restore_data(data)
   
# Register the custom command group with the Flask application
app.cli.add_command(custom_cli)
       
# this runs the flask application on the development server
if __name__ == "__main__":
    # change name for testing
    app.run(debug=True, host="0.0.0.0", port=8402)
