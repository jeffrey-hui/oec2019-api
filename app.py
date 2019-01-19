from flask import Flask, request, jsonify, redirect, url_for, session, logging, send_from_directory
from flask_cors import CORS
import pymongo
from pymongo import MongoClient
import json
from passlib.hash import sha256_crypt
import datetime
import os
from twilio.rest import Client

# MediHelper API
'''
The Medihelper API allows users to report medical checkup data to the database 
and allow healthcare professionals to quickly screeen issues to determine if a follow up
is required.
'''

# Database Connection Setup
user = os.environ.get('URI_USER')
password = os.environ.get('URI_PASS')

client = Client(account_sid, auth_token)
uri = 'mongodb://' + user + ':' + password + '@ds161104.mlab.com:61104/ryeoec2019'
client = MongoClient(uri, connectTimeoutMS=30000)
db = client.get_database("ryeoec2019")
hospital = db.hospital

# Application Startup
app = Flask(__name__)
CORS(app)

@app.route('/create_doctor', methods=['GET','POST'])
def create_doctor():
	if request.method == 'POST':
		name = request.form['name']
		password = request.form['password']
		post_data = {
    		'docname': name,
    		'password': sha256_crypt.hash(password),
    		'date': datetime.datetime.utcnow()
    	}
		result = hospital.insert_one(post_data)
		return "<h1>Doctor Profile Created!</h1>"
	return "Invalid"

# .../text?to=16479998765&message="please%20work"
@app.route('/text'):
def text():
	text_to = request.args.get('to')
	message = request.args.get('message')
	account_sid = os.environ.get('TWIL_SID')	
	auth_token = os.environ.get('TWIL_TOKEN')
	text_from = os.environ.get('FROM')
	client2 = Client(account_sid, auth_token)

	client2.messages \
	                .create(
	                     body='please work',
	                     from_=text_from,
	                     to='14169027388'
	                 )
	return "Sent"


@app.route('/send', methods=['GET','POST'])
def send():
	if request.method == 'POST':
		name = request.form['name']
		gender = request.form['gender']
		pnumber = request.form['phonenumber']
		symptoms = request.form['symptoms']
		doctor = request.form['doctor']
		apptdate = request.form['apptdate']
		post_data = {
    		'name': name,
    		'gender': gender,
    		'pnumber': pnumber,
    		'symptoms': symptoms,
    		'doctor': doctor,
    		'apptdate': apptdate,
    		'date': datetime.datetime.utcnow()
    	}
		result = hospital.insert_one(post_data)
		return "<h1>Your Message has been recieved by our service and your physician will be in touch shortly</h1>" 
	return "<h1>Something went wrong! Please click back and try again!</h1>"

@app.route("/api")
def api():
	return "/send - POST client data <br/> /login - POST Doctors Login"


# Doctors must be added to the database via IT Services
# Contact IT for new doctor onboarding
@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		name = request.form['name']
		password = request.form['password']
		if hospital.find_one({"docname": name}) != None:
			try_login = hospital.find_one({"docname": name})
			if sha256_crypt.verify(password, try_login['password']):
				patient_names = []
				genders = []
				pnumbers = []
				symptoms = []
				doctors = []
				apptdates = []
				for patient in hospital.find({"doctor": name }):
					patient_names.append(patient['name'])
					genders.append(patient['gender'])
					pnumbers.append(patient['pnumber'])
					symptoms.append(patient['symptoms'])
					doctors.append(patient['doctor'])
					apptdates.append(patient['apptdate'])
				return jsonify({"names": patient_names, "genders": genders, "phonenumbers": pnumbers, "symptoms": symptoms, "doctors": doctors, "apptdates": apptdates})
	return "Failed"

if __name__ == "__main__":
	app.run()
