#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@project= elasticd
@file= __init__.py
@author= wubingyu
@create_time= 2018/3/15 上午11:16
"""
from flask import Flask, _app_ctx_stack, url_for, redirect, flash, render_template, request, session, abort
import sqlite3
import os
import logstash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'schema.db'),
	SECRET_KEY='development',
	DEBUG=True,
	username='admin',
	password='default',
	logstash_path='/Users/wubingyu/PycharmProjects/Projects/2.7.11/elasticd/first-pipeline.conf'
))

app.config.from_envvar('FLASK_ENV', silent=True)


def get_db():
	""" get the sqlite from  app.config.DATABASE"""
	top = _app_ctx_stack.top
	if not hasattr(top, "sqlite"):
		top.sqlite = sqlite3.connect(app.config['DATABASE'])
		top.sqlite.row_factory = sqlite3.Row
	return top.sqlite


def init_db():
	""" initialing the database"""
	db = get_db()
	with app.open_resource("schema.sql", mode="r") as f:
		db.cursor().executescript(f.read())
	db.commit()


@app.cli.command('initdb')
def initdb_command():
	init_db()
	print 'Initialized Database'


def query_db(query, args=(), one=False):
	rv = get_db().execute(query, args).fetchall()
	return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def teardown(error):
	top = _app_ctx_stack.top
	if hasattr(top, "sqlite"):
		top.sqlite.close()


@app.route('/')
def index():
	settings = query_db("select id,title,content from settings order by id DESC ")
	return render_template('show_settings.html', settings=settings)


@app.route('/login', methods=['POST', 'GET'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['username']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['password']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in!')
			return redirect(url_for('settings_list'))
	return render_template('login.html', error=error)


@app.route('/settings/list')
def settings_list():
	settings = query_db('SELECT id,title,content FROM settings ORDER BY id DESC ')
	return render_template('show_settings.html', settings=settings)


@app.route('/settings/delete/<int:setting_id>')
def setting_delete(setting_id):
	if not session.get("logged_in"):
		error = 'please login in first!'
		return render_template('login.html', error=error)
	db = get_db()
	db.execute("delete from settings where id =" + str(setting_id))
	db.commit()
	flash("You already delete the setting!")
	return redirect(url_for('settings_list'))


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out!')
	return redirect(url_for('settings_list'))


@app.route('/setting/add', methods=['POST'])
def setting_add():
	if not session.get("logged_in"):
		abort(401)
	db = get_db()
	db.execute('INSERT INTO settings (title,content)VALUES (?,?)', [request.form['title'], request.form['content']])
	db.commit()
	return redirect(url_for('settings_list'))


@app.route('/servers/list')
def servers_list():
	servers = query_db('select * from servers order by id DESC ')
	return render_template('show_servers.html', servers=servers)


@app.route('/servers/add', methods=['POST'])
def servers_add():
	if not request.form['ip']:
		error = 'please input the server ip'
	elif not session.get('logged_in'):
		error = 'please log in first!'
	else:
		db = get_db()
		db.execute('INSERT INTO servers(ip,role,password) VALUES (?,?,?)',
				   [request.form['ip'], request.form['role'], request.form['password']])
		db.commit()
		return redirect(url_for('servers_list'))
	return redirect(url_for('login'), error=error)


@app.route('/servers/delete/<int:server_id>')
def servers_delete(server_id):
	if not session.get('logged_in'):
		error = 'please log in first'
		return render_template('login.html', error=error)
	db = get_db()
	db.execute('delete FROM servers where id =' + str(server_id))
	db.commit()
	flash('You already delete the server')
	return redirect(url_for('servers_list'))


@app.cli.command('initlogtash')
def init_logstash():
	logstash.open_settings()
	print "initialized the logstash setting"


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
