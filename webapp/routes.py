from flask import request, render_template, redirect, flash, url_for, jsonify, send_from_directory
from webapp import app, db, bc, bcrypt, login_manager, socketio
from webapp.models import User, Transaction_history, Transaction_pool, Notifications
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import emit
import yaml
from webapp.utils import gen_sk, gen_hash, sign_data, jsonify_blockchain, allowed_file
from webapp.block import Block
from webapp.blockchain import Blockchain
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import shutil

with open('webapp/config.yaml') as stream:
	yaml_dict = yaml.safe_load(stream) 	

INITIAL_BALANCE = yaml_dict['INITIAL_BALANCE']
PATH_TO_WEBAPP = app.root_path
PATH_TO_DOWNLOAD = os.path.join(PATH_TO_WEBAPP, app.config['DOWNLOAD_FOLDER'])


@socketio.on('Broadcast Blockchain')
def broadcast_bc(json_bc):
	emit('Broadcast Blockchain', json_bc, broadcast=True)


@app.route("/")
@app.route("/home", methods=['GET'])
def home():
	if current_user.is_authenticated:
		return redirect('/account', code=302)
	return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return render_template('account.html', code=302)

	if request.method == 'GET':
		return render_template('signup.html')

	if request.method == 'POST':
		result = request.form

		user =  User.query.filter_by(username=result['signup_name']).first() or \
			User.query.filter_by(usermail=result['signup_email']).first()

		if user:
			flash("User already exist", 'info')
			return redirect('/login', code=302)

		hashed_pswd = bcrypt.generate_password_hash(result['signup_pswd']).decode('utf-8')

		sk = gen_sk()

		user = User(username=result['signup_name'],
			usermail=result['signup_email'],
			userpwd=hashed_pswd,
			userbal=INITIAL_BALANCE,
			usersk=sk.to_string().hex(),
			uservk=sk.verifying_key.to_string('uncompressed').hex())

		db.session.add(user)
		db.session.commit()

		name = result['signup_email']
		flash(f'Hello {name}, your account has been created.', 'success')
		return redirect('/login', code=302)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return render_template('account.html', code=302)

	if request.method == 'GET':
		return render_template('login.html')

	if request.method == 'POST':
		result = request.form
		user = User.query.filter_by(usermail=result['login_email']).first()

		if not user:
			flash("User does not exist", 'danger')
			return redirect('/signup', code=302)

		if not bcrypt.check_password_hash(user.userpwd, result['login_pswd']):
			flash("User password is incorrect", 'danger')
			return redirect('/login', code=302)

		try:
			login_user(user, remember=result['remember'])
		except:
			login_user(user, remember=False)

		flash(f'welcome {user.username}', 'success')
		return redirect('/account', code=302)

# Feature 1
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	return render_template('account.html')


@app.route('/viewacc')
@login_required
def viewacc():
	return render_template('viewacc.html')

@app.route('/details_acc')
@login_required
def details_acc():
	return render_template('details_acc.html', )

@app.route('/transact_details')
@login_required
def transact_details():
	return render_template('transact_details.html', Transaction_history=Transaction_history)


# Feature 2
@app.route('/notification', methods=['GET', 'POST'])
@login_required
def notification():
	if request.method == 'GET':
		return render_template('notification.html', Notifications=Notifications)

	if request.method == 'POST':
		result = request.form
		time = result['timestamp']

		if result['bt'] == 'Sent':

			if float(result['amount']) > current_user.userbal:
				flash('The amount exceeds the balance', 'danger')
				return redirect('/send_crypto', code=302)

			if not User.query.filter_by(uservk=result['recipient_address']).first():
				flash('Unknown recipient address', 'danger')
				return redirect('/peers', code=302)

			data = {
			'timestamp': time,
			'sender_address': current_user.uservk,
			'recipient_address': result['recipient_address'],
			'amount': result['amount']
			}

			data_hash = gen_hash(data)

			transaction_pool = Transaction_pool(
				timestamp=time,
				sender_address=current_user.uservk,
				recipient_address=result['recipient_address'],
				amount=result['amount'],
				signature=sign_data(current_user.usersk, data_hash),
				userid=current_user.userid)

			db.session.add(transaction_pool)
			db.session.commit()

			flash('Successfuly added the transaction in the pool', 'success')

		elif result['bt'] == 'Rejected':
			transaction_history = Transaction_history(
				timestamp=time,
				Action=result['bt'],
				sender_address=current_user.uservk,
				recipient_address=result['recipient_address'],
				amount=result['amount'],
				signature='None',
				userid=current_user.userid)

			db.session.add(transaction_history)
			db.session.commit()

			flash(f"Transaction status: {result['bt']}", 'info')

		else:
			transaction_history = Transaction_history(
				timestamp=time,
				Action=result['bt'],
				sender_address=result['sender_address'],
				recipient_address=current_user.uservk,
				amount=result['amount'],
				signature='None',
				userid=current_user.userid)

			db.session.add(transaction_history)
			db.session.commit()

			flash(f"Transaction status: {result['bt']}", 'info')

		del_record = db.session.query(Notifications).filter(
			Notifications.tid==result['notification_id']).one()
		db.session.delete(del_record)
		db.session.commit()

		if result['bt'] == 'Sent': 
			return redirect('/transaction_pool', code=302)
		else:
			return redirect('/account', code=302)

# Feature 3
@app.route('/send_crypto', methods=['GET', 'POST'])
@login_required
def send_crypto():
	if request.method == 'GET':
		return render_template('send_crypto.html')
	
	if request.method == 'POST':
		result = request.form

		if float(result['amount']) > current_user.userbal:
			flash('The amount exceeds the balance', 'danger')
			return redirect('/send_crypto', code=302)

		if not User.query.filter_by(uservk=result['vk']).first():
			flash('Unknown recipient address', 'danger')
			return redirect('/peers', code=302)

		if result['vk']==current_user.uservk:
			flash('Can not send crypto to self', 'danger')
			return redirect('/peers', code=302)

		time = datetime.now().strftime("%d/%m/%y,%H:%M:%S")

		data = {
		'timestamp': time,
		'sender_address': current_user.uservk,
		'recipient_address': result['vk'],
		'amount': result['amount']
		}

		data_hash = gen_hash(data)

		transaction_pool = Transaction_pool(
			timestamp=time,
			sender_address=current_user.uservk,
			recipient_address=result['vk'],
			amount=result['amount'],
			signature=sign_data(current_user.usersk, data_hash),
			userid=current_user.userid)

		db.session.add(transaction_pool)
		db.session.commit()

		flash('Successfuly added the transaction in the pool', 'success')
		return redirect('/transaction_pool', code=302)

# Feature 4
@app.route('/receive_crypto', methods=['GET', 'POST'])
@login_required
def receive_crypto():
	if request.method == 'GET':
		return render_template('receive_crypto.html')
	
	if request.method == 'POST':
		result = request.form

		sender_user = User.query.filter_by(uservk=result['vk']).first()
		
		if not sender_user:
			flash('The user does not exist', 'danger')
			return redirect('/peers', code=302)

		if result['vk'] == current_user.uservk:
			flash('Can not receive crypto from self', 'danger')
			return redirect('/peers', code=302)

		if float(result['amount']) > sender_user.userbal:
			flash('The transaction has bounced', 'danger')
			return redirect('/receive_crypto', code=302)

		time = datetime.now().strftime("%d/%m/%y,%H:%M:%S")

		notification = Notifications(
			timestamp=time,
			sender_address=result['vk'],
			recipient_address=current_user.uservk,
			amount=result['amount'],
			userid=current_user.userid)

		db.session.add(notification)
		db.session.commit()

		flash('Request sent to the sender', 'info')
		return redirect('/notification', code=302)

# nav bar
@app.route('/viewbc')
@login_required
def viewbc():
	return render_template('viewbc.html', bc=jsonify_blockchain(bc))

@app.route('/peers')
@login_required
def peers():
	return render_template('peers.html', User=User)

@app.route('/transaction_pool')
@login_required
def transaction_pool():
	return render_template('transaction_pool.html', Transaction_pool=Transaction_pool)

@app.route('/start_mine', methods=['POST','GET'])
@login_required
def start_mine():
	if request.method == 'POST':

		result = request.form
		tp_data = dict((key, request.form.getlist(key)) for key in request.form.keys())

		number_of_transactions = len(tp_data['timestamp'])

		tp_sign = []

		for index, sender_address in enumerate(tp_data['sender_address']):  
			sender = User.query.filter_by(uservk=sender_address).first()

			data_hash = gen_hash([tp_data[key][index] for key in request.form.keys()])
			signed_data = sign_data(sender.usersk, data_hash)

			tp_sign.append(signed_data)

		json_bc = jsonify_blockchain(bc)

		if not os.path.exists(PATH_TO_DOWNLOAD):
			os.mkdir(PATH_TO_DOWNLOAD)

		# Save hash data 
		with open(PATH_TO_DOWNLOAD+'/data_hash.txt', "w") as file:
			file.write(b"".join(tp_sign).hex())

		# Save blockchain 
		with open(PATH_TO_DOWNLOAD+'/bc.json', "w") as file:
			json.dump(json_bc, file)

		shutil.make_archive('Download_Blockchain', 'zip', PATH_TO_DOWNLOAD)

		flash("Select Mine from the Navbar", 'info')

		return send_from_directory(directory=PATH_TO_WEBAPP[:-7], path='Download_Blockchain.zip', as_attachment=True, cache_timeout=0)

@app.route('/mine')
def mine():
	return render_template('mine.html')

@app.route('/upload_bc', methods=['GET', 'POST'])
def upload_bc():

	if request.method == 'POST':

		file = request.files['file']

		if file.filename == '':
		    flash('No selected file', 'info')
		    return redirect('/mine')

		if file and allowed_file(file.filename):
		    filename = secure_filename(file.filename)
		    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		    return redirect('/verify_and_replace_bc')
		else:
			flash("Choose correct extension", 'danger')
			return redirect('/mine')
	
@app.route('/verify_and_replace_bc')
def verify_and_replace_bc():

	with open(os.path.join(app.config['UPLOAD_FOLDER'], 'output.json'), 'r') as f:
		bc_json = json.load(f)

	temp_bc = Blockchain()

	for key, value in bc_json.items():
		block = Block(
			value['timestamp'], 
			value['prev_hash'], 
			value['data'], 
			value['present_hash'], 
			value['nonce'], 
			value['difficulty'])
		
		if key == 'Block 0':
			temp_bc.chain[0] = block
		else:
			temp_bc.chain.append(block)

	if bc.replace_chain(temp_bc):
		transaction_pool = Transaction_pool.query.all()

		for tp in transaction_pool:
			time = datetime.now().strftime("%d/%m/%y,%H:%M:%S")

			# Remove from Transaction Pool
			sender_address = tp.sender_address
			recipient_address = tp.recipient_address
			amount = tp.amount
			userid = tp.userid
			signature = tp.signature
			userid = tp.userid

			db.session.delete(tp)
			db.session.commit()

			# Add in Transaction History
			transaction_history = Transaction_history(
				timestamp=time,
				Action='Sent',
				sender_address=sender_address,
				recipient_address=recipient_address,
				amount=amount,
				signature=signature,
				userid=userid)

			db.session.add(transaction_history)
			db.session.commit()

			# Update balance
			user_sender = User.query.filter_by(uservk=sender_address).first()
			user_recipient = User.query.filter_by(uservk=recipient_address).first()

			user_sender.userbal = user_sender.userbal - amount
			user_recipient.userbal = user_recipient.userbal + amount

			db.session.commit()


		flash("Successfuly added", 'success')
		return redirect('/viewbc')

	else:
		flash("Something went wrong", 'danger')
		return redirect('/transaction_pool')

@app.route('/logout', methods=['GET', 'POST'])
def logout():

	if current_user.is_authenticated:
		logout_user()

	return redirect('/', code=302)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')