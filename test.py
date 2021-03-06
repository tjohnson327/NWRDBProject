#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 00:06:53 2018
@author: Tyler Johnson and Sean Pergola
"""

from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
from passlib.hash import sha256_crypt
from clubs import clubs
import yagmail

app = Flask(__name__)

templates = {
	"login": "DataBaseLogin1.html",
	"makeuser": "Signup page.html",
	"dataEntry": "index.htm",
	"clubList": "DatabaseClubList1.html",
	"clubListNoUser": "Clublist2.html",
	"user": "UserPageDatabase.html",
	"404": "errorpage404.html",
	"admin": "adminPage.html",
}

pointer = "»"

app.secret_key = "53Da__de39^^w32$5)*8"

userTableFields = """ (
	name varchar(255) NOT NULL PRIMARY KEY,
	hours integer NOT NULL,
	approved integer NOT NULL
	); """

def fixName (clubName):
	for char in clubName:
		if char == '-':
			char = '〰'
			continue
		if char == '〰':
			char = '-'

def refreshEntries():
	conn = sqlite3.connect('database.db')
	cur = conn.cursor()
	username = session['user'][0]
	entries = []
	for i,row in enumerate(cur.execute("SELECT * FROM userEntries")):
		entries.append(row)

	session['entries'] = entries


	conn.commit()
	conn.close()

@app.route('/')
def index():
	return 'Index Page'

@app.route('/hello')
def hello():
	return 'Hello, World'

@app.route('/dataentry/', methods=["POST", "GET"])
def dataEntry():
	if (request.method=="POST"):
		user = session['user']
		conn = sqlite3.connect('database.db')
		cur = conn.cursor()
		entry = [session['user'][0], request.form['club'], request.form['activity'], int(request.form['hours']), int(request.form['approved'])]
		cur.execute("INSERT INTO userEntries VALUES(?,?,?,?,?)", entry)
		conn.commit()
		conn.close()
		return "Sent."
	elif ('user' in session):
		user = session['user']
		username = user[0]
		return render_template(templates["dataEntry"], username=username)
	else:
		return redirect("/login")

@app.route('/entrylist/')
def viewEntries():
	conn = sqlite3.connect('database.db')
	cur = conn.cursor()
	users = cur.execute("SELECT * FROM userEntries")

	names=[]
	club=[]
	activity=[]
	hours=[]
	approved=[]
	for row in users:
		names.append(row[0])
		club.append(row[1])
		activity.append(row[2])
		hours.append(row[3])
		approved.append(row[4])

	return render_template('entrylist.html', names=names, clubs=club, activities=activity, hours=hours, approved=approved)



@app.route('/clubs', methods=["POST", "GET"])
def clublist():
	conn = sqlite3.connect('database.db')
	cur = conn.cursor()
	if (request.method=="POST"):
		wantedclub = request.form['club']
		temparray = fixArray(session['user'][3],False)
		newtemparray = []
		username = session['user'][0]
		print(temparray)


		for each in temparray:
			newtemparray.append(each.name)

		newtemparray.append(wantedclub)

		exlist = (str(newtemparray), session['user'][0])
		cur.execute("UPDATE users SET memberships = ? WHERE username = ?", exlist)

		conn.commit()
		conn.close()


		return render_template(templates["clubList"], clublist=clubs.getAll(), username=username,adminlevel=session['user'][2], memberships=exlist)
	else:
		try:
			username = session['user'][0]
			return render_template(templates["clubList"], clublist=clubs.getAll(), username=username,adminlevel=session['user'][2], memberships=session['user'][3])
		except KeyError:
			return render_template(templates["clubListNoUser"], clublist=clubs.getAll())


@app.route('/user', methods=["POST","GET"])
def viewUser():
	if (request.method=="POST"):
		user = session['user']
		conn = sqlite3.connect('database.db')
		cur = conn.cursor()
		entry = [session['user'][0], request.form['club'], request.form['activity'], int(request.form['hours']), 0]
		cur.execute("INSERT INTO userEntries VALUES(?,?,?,?,?)", entry)
		conn.commit()
		conn.close()

		refreshEntries()
		return redirect("/user")
	elif (request.method=="GET" and 'user' in session):
		user = session['user']
		username = user[0] #SEAN ES MUY STUPIDO
		adminLevel = user[2]
		rawMemberships = user[3]

		memberships = fixArray(rawMemberships, False)

		refreshEntries()

		return render_template(templates["user"], username=username,adminlevel=adminLevel,memberships=memberships)

	else:
		return redirect('/login')

@app.route('/admin', methods=["GET", "POST"])
def viewAdmin():
	if request.method == "GET":
		if 'user' in session:
			user = session['user']
			if user[2] != 0:
				advisories = fixArray(user[4], True)

				return render_template(templates['admin'],adminlevel=session['user'][2],username=session['user'][0],advisories=advisories)
			else:
				return redirect('/user')
		else:
			return redirect('/login')
	elif request.method == "POST":
		return "TODO: Implement post method"

@app.route('/html')
def html():
	return render_template('test.html', name='Sean')

def fixArray(array, admin):
	user = session['user']
	rawArray = array.split(",")
	entries = session['entries']

	array_ = []

	array = []

	arrayClubs = []

	if rawArray != ['[]']:
		#strip unnecessary characters for memberships
		for each in rawArray:
			i = 0
			length = len(each)
			while i < length:
				if each[i] == " ":
					each = each[:i] + each[i+1:]
				if each[i] == "[":
					each = each[:i] + each[i+1:]
				if each[i] == "]":
					each = each[:i] + each[i+1:]
				if each[i] == "'":
					each = each[:i] + each[i+1:]
				i += 1
				length = len(each)
			each = each[:len(each)]
			array_.append(each)

		#STUPID JANK FIX FOR END OF ARRAY ']'
		last = array_[len(array_)-1]
		lastLen = len(last)-1
		if last[lastLen] == "]":
			last = last[:lastLen]

		array_.pop(len(rawArray)-1)
		array_.append(last)

		last = rawArray[len(rawArray)-1]
		lastLen = len(last)-1

		#replace '_' with spaces for memberships
		for each in array_:
			for i in range(len(each)-1):
				if i < len(each):
					if each[i] == "_":
						each = each[:i] + " " + each[i+1:]
			each = each[:len(each)]
			array.append(each)
	else:
		array.append("None")

	#create membership club array from membership string array
	for each in array:
		club = clubs(each)
		for entry in entries:
			if club.name == entry[1]:
				if user[0] == entry[0] or admin:
					club.addEntry(entry)

		arrayClubs.append(club)

	return arrayClubs

@app.route('/login', methods=["POST", "GET"])
def login():
	if (request.method=="POST"):
		conn = sqlite3.connect('database.db')
		cur = conn.cursor()
		username = request.form['username']
		password = request.form['password']
		user = None
		for row in cur.execute("SELECT * FROM users"):
			if row[0] == username:
				user = row

		if user == None:
			return render_template(templates["login"], incorrect=True)


		if (sha256_crypt.verify(password, user[1]) == True):
			session['user'] = user
			refreshEntries()
		else:
			return render_template(templates["login"], incorrect=True)

		return redirect('/user')
	else:
		return render_template(templates["login"], incorrect=False)

@app.route('/userlist')
def userlist():
	conn = sqlite3.connect('database.db')
	cur = conn.cursor()
	users = cur.execute("SELECT * FROM users")

	names=[]
	passwords=[]
	levels=[]
	memberships=[]
	advisories=[]
	for row in users:
		names.append(row[0])
		passwords.append(row[1])
		levels.append(row[2])
		memberships.append(row[3])
		advisories.append(row[4])

	return render_template('userlist.html', names=names, passwords=passwords, levels=levels, memberships=memberships, advisories=advisories)

@app.route('/makeuser', methods=["POST", "GET"])
def makeuser():
	if (request.method=="POST"):
		conn = sqlite3.connect('database.db')
		cur = conn.cursor()
		attemptusername = request.form['username']

		attemptpass = request.form['password']
		numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
		passfail = False
		for each in numbers:
			if each in attemptpass:
				passfail = False
				break
			else:
				passfail = True
		if not passfail:
			if lower(attemptpass) == attemptpass or upper(attemptpass) == attemptpass:
				passfail = True

		for row in cur.execute("SELECT * FROM users"):
			if row[0] == attemptusername:
				userfail = True

		userinfo = [request.form['username'], sha256_crypt.hash(request.form['password']), int(request.form['adminLevel']), str(request.form.getlist('memberships')), str(request.form.getlist('advisories'))]
		cur.execute("INSERT INTO users VALUES (?,?,?,?,?)", userinfo)
		conn.commit()
		conn.close()
		return render_template(templates["makeruser"], passfail = passfail, userfail = userfail, success = (passfail or userfail))
	else:
		return render_template(templates["makeuser"])

@app.errorhandler(404)
def fourohfour(e):
	test = request.path
	for tempurl in app.url_map.iter_rules():
		if str.lower(test) == str.lower(str(tempurl)):
			return redirect(str(tempurl)) #TODO: Fix 404 for /USER

	return render_template(templates["404"], url=str(test))

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/login')

@app.route('/testemail')
def sendemail():
	yag = yagmail.SMTP()
	contents = "Hello world"
	yag.send('seanpergola@gmail.com', 'Yagmail test', contents)
	return 'Email sent to seanpergola@gmail.com'
