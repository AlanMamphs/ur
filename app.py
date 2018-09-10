import json
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, send_from_directory
from models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
import os


photos = UploadSet('photos', IMAGES)

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
configure_uploads(app, photos)

db.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route("/")
@login_required
def index():
	return render_template("index.html", user=current_user)

@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == 'POST':
		username = request.form.get("username")
		password = request.form.get("password")
		email = request.form.get("email")
		name = request.form.get("name")
		surname = request.form.get("surname")
		mobile = request.form.get("mobile")
		birthday = request.form.get("birthday")

		user = User.query.filter(User.username.ilike(username)).first()
		user_email = User.query.filter(User.email.ilike(email)).first()
		data = json.dumps(request.form.to_dict())

		if not user and not user_email:
			password = generate_password_hash(password, method="sha256")
			new_user = User(username=username, password=password, email=email, name=name,
						surname=surname, mobile=mobile, birthday=birthday)
			db.session.add(new_user)
			db.session.commit()
			flash(u"You have successfully registered! Please login with your new credentials", 'success')
			return redirect(url_for('index'))

		elif user:
			flash(u"This user already exists!", 'error')
			return render_template('register.html', data=json.loads(data))
			
		elif email:
			print(request.form.to_dict(flat=False))	
			flash(u"This email is already in use", 'error')
			return render_template('register.html', data=json.loads(data))


	return render_template('register.html', data=data)

@app.route("/update/<string:username>/<string:data>", methods=["POST"])
def update(username, data):
	if request.method == 'POST':
		user = User.query.filter_by(username=username).first()

		if data == 'info':

			email = request.form.get("email")
			user_email = User.query.filter(User.email.ilike(email)).first()
			if not user_email or user.email == email:

				user.name = request.form.get("name")
				user.surname = request.form.get("surname")
				user.mobile = request.form.get("mobile")
				user.email = email
				flash(u"Successfully updated personal info!", 'success')
				db.session.commit()

			else:
				flash(u"This email is already in use", 'error')
			
			return redirect(url_for('profile', username=username))

		if data == 'password':
			password = request.form.get("old_password")
			if check_password_hash(user.password, password):
				new_password = request.form.get("password")
				new_password = generate_password_hash(new_password, method="sha256")
				user.password = new_password

				db.session.commit()
				flash(u"Successfully updated password", 'success')
			else:
				flash(u"Invalid password", 'error')

			return redirect(url_for('profile', username=current_user.username))
		
	return redirect(url_for('profile', username=current_user.username))




@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		user = User.query.filter(User.username.ilike(username)).first()

		if user:
			if check_password_hash(user.password, password):
				login_user(user)
				flash(u"You have successfully logged in!", 'success')
				return redirect(url_for('index'))
			else:
				flash(u"Invalid password!", 'error')
		else:
			flash(u"Invalid username!", 'error')
	return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/profile/<string:username>', methods=['GET', 'POST'])
@login_required
def profile(username):
	user = User.query.filter_by(username=username).first()
	print (user)
	if request.method == 'POST' and 'file' in request.files:
		filename = photos.save(request.files['file'])
		user.profile_img = filename
		db.session.commit()
		flash(u"Image Uploaded", 'success')
		return redirect(url_for('profile', username=username))
	return render_template('edit.html', user=user)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'],
                               filename)
if __name__ == '__main__':
    app.run()
    