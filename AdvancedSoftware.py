# all the imports
from __future__ import  with_statement
from contextlib import closing
from datetime import datetime
import sqlite3
import os;
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

# configuration
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'tmp', 'flaskr.db')
DEBUG = True

SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()

def get_posts():
    size = 0

    if session.get('logged_in'):
        cur = g.db.execute('select * from boards where id = ? and btype= ?', [session['id'], '0'])
        row = cur.fetchall()
        size = len(row)

    return size

def get_email():
    email = ''

    if session.get('logged_in'):
        cur = g.db.execute('select email from users where id = ?', [session['id']])
        row = cur.fetchall()
        email = row[0][0]

    return email

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_dashboard():
    id = ''
    works = get_posts()
    email = get_email()

    team_doneEntries = None
    team_doingEntries = None
    team_todoEntries = None

    my_doneEntries = None
    my_doingEntries = None
    my_todoEntries = None

    members = None
    notice = ''

    if session.get('logged_in'):

        cur3 = g.db.execute('select subject, username, writedate, ctype from boards where id = ? and btype = ?',
                            [session['id'], '-1'])
        result3 = cur3.fetchall()

        my_doneEntries = [dict(subject=row[0], username=row[1], writedate=row[2]) for row in result3 if row[3] == 'done']
        my_doingEntries = [dict(subject=row[0], username=row[1], writedate=row[2]) for row in result3 if row[3] == 'doing']
        my_todoEntries = [dict(subject=row[0], username=row[1], writedate=row[2]) for row in result3 if row[3] == 'todo']

        id = session['id']
        query = g.db.execute('select notice, no from teams where name = ?', [session['curteam']])
        temp = query.fetchall()

        if len(temp) != 0:
            notice = temp[0][0]

            cur = g.db.execute('select subject, username, writedate, ctype from boards where btype = ?', [temp[0][1]])
            result = cur.fetchall()

            team_doneEntries = [dict(subject=row[0], username=row[1], writedate=row[2]) for row in result if row[3] == 'done']
            team_doingEntries = [dict(subject=row[0], username=row[1], writedate=row[2]) for row in result if row[3] == 'doing']
            team_todoEntries = [dict(subject=row[0], username=row[1], writedate=row[2]) for row in result if row[3] == 'todo']

            cur2 = g.db.execute('select username from users where curteam = ?', [session['curteam']])
            result2 = cur2.fetchall()

            members = result2

            return render_template('dashboard.html', works=works, id=id, email=email,
                           team_doneEntries=team_doneEntries, team_doingEntries=team_doingEntries, team_todoEntries=team_todoEntries, members=members,
                                   my_doneEntries=my_doneEntries, my_doingEntries=my_doingEntries, my_todoEntries=my_todoEntries, notice=notice, teamname=session['curteam'])

        return render_template('dashboard.html', works=works, id=id, email=email,
                               my_doneEntries=my_doneEntries, my_doingEntries=my_doingEntries,
                               my_todoEntries=my_todoEntries)

    return render_template('dashboard.html', works=works, id=id, email=email)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    works = get_posts()
    id = ''

    if request.method == 'POST':
        cur = g.db.execute('select password, username, curteam from users where id = ?', [request.form['id']])
        row = cur.fetchall()

        if len(row) == 0:
            error = 'No such user'
        else:
            if request.form['password'] != row[0][0]:
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                session['id'] = request.form['id']
                id = session['id']
                session['username'] = row[0][1]
                session['curteam'] = row[0][2]
                flash('You were logged in')
                return render_template('dashboard.html', works=works, id=id)

    return render_template('dashboard.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        cur = g.db.execute('select * from users where id= ?', [request.form['id']])
        row = cur.fetchall()

        if len(row) != 0:
            error = 'Id is already taken'
        else:
            g.db.execute('insert into users (id, username, password, email, mobile) values (?, ?, ?, ?, ?)',
                         [request.form['id'], request.form['username'], request.form['password'], request.form['email'], request.form['mobile']])
            g.db.commit()
            flash('you are registered')
            return render_template('dashboard.html')

    return render_template('register.html', register_error=error)


@app.route('/team_works')
def team_works():
    doneEntries = None
    doingEntries = None
    todoEntries = None

    members = None

    works = get_posts()
    email = get_email()
    id = ''

    if session.get('logged_in'):
        id = session['id']

        query = g.db.execute('select * from teams where name = ?', [session['curteam']])
        temp = query.fetchall()

        print(temp)

        if len(temp) != 0:
            cur = g.db.execute('select subject, content, username, writedate, ctype from boards where btype = ?', [temp[0][0]])
            result = cur.fetchall()

            doneEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'done']
            doingEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'doing']
            todoEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'todo']

            cur2 = g.db.execute('select username from users where curteam = ?', [session['curteam']])
            result2 = cur2.fetchall()

            members = result2

            return render_template('team_works.html', doneEntries=doneEntries, doingEntries=doingEntries, todoEntries=todoEntries, works=works, id=id, email=email, teamname=session['curteam'], members=members)

    return render_template('team_works.html', works=works, id=id, email=email)


@app.route('/config_team', methods=['POST'])
def config_team():
    error = None

    if (request.form['submit'] == 'create'):
        cur = g.db.execute('select * from teams where name= ?', [request.form['teamname']])
        row = cur.fetchall()

        if len(row) != 0:
            error = 'Teamname is already taken'
        else:
            print(request.form)
            g.db.execute('insert into teams (name, password) values (?, ?)', [request.form['teamname'], request.form['teampassword']])
            g.db.commit()

            print('b')
            g.db.execute('update users set curteam = ? where id= ?', [request.form['teamname'], session['id']])
            g.db.commit()
            print('c')
            session['curteam'] = request.form['teamname']
    elif (request.form['submit'] == 'join'):
        cur = g.db.execute('select * from teams where name= ? and password = ?', [request.form['teamname'], request.form['teampassword']])
        row = cur.fetchall()

        print(request.form)
        if len(row) == 0:
            error = 'Team is not exist'
        else:
            g.db.execute('update users set curteam = ? where id= ?', [request.form['teamname'], session['id']])
            g.db.commit()
            session['curteam'] = request.form['teamname']
    elif (request.form['submit'] == 'leave'):
        g.db.execute('update users set curteam = ? where id= ?', ['', session['id']])
        g.db.commit()
        session['curteam'] = ''

    doneEntries = None
    doingEntries = None
    todoEntries = None
    members = None

    works = get_posts()
    email = get_email()
    id = ''

    if session.get('logged_in'):
        id = session['id']

        query = g.db.execute('select * from teams where name = ?', [session['curteam']])
        temp = query.fetchall()

        print(temp)

        if len(temp) != 0:
            cur = g.db.execute('select subject, content, username, writedate, ctype from boards where id = ? and btype = ?', [session['id'], temp[0][0]])
            result = cur.fetchall()

            doneEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'done']
            doingEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'doing']
            todoEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'todo']

            cur2 = g.db.execute('select username from users where curteam = ?', [session['curteam']])
            result2 = cur2.fetchall()

            members = result2[0];
            print(members)

            return render_template('team_works.html', doneEntries=doneEntries, doingEntries=doingEntries, todoEntries=todoEntries, works=works, id=id, email=email, teamname=session['curteam'], members=members)

    return render_template('team_works.html', works=works, id=id, email=email, teamname=session['curteam'], error=error)


@app.route('/change_notice', methods=['POST'])
def change_notice():
    cur = g.db.execute('select no from teams where name= ?', [session['curteam']])
    row = cur.fetchall()

    if len(row) != 0:
        g.db.execute(
            'update teams set notice = ? where name = ?',
            [request.form['notice'], session['curteam']])
        g.db.commit()

    return team_works()


@app.route('/my_works')
def my_works():
    doneEntries = None
    doingEntries = None
    todoEntries = None

    works = get_posts()
    email = get_email()
    id = ''

    if session.get('logged_in'):
        id = session['id']

        cur = g.db.execute('select subject, content, username, writedate, ctype from boards where id = ? and btype = ?', [session['id'], '-1'])
        result = cur.fetchall()

        doneEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'done']
        doingEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'doing']
        todoEntries = [dict(subject=row[0], content=row[1], username=row[2], writedate=row[3]) for row in result if row[4] == 'todo']

        return render_template('my_works.html', doneEntries=doneEntries, doingEntries=doingEntries, todoEntries=todoEntries, works=works, id=id, email=email )

    return render_template('my_works.html', works=works, id=id, email=email)

@app.route('/add_my_works', methods=['POST'])
def add_my_works():
    error = None

    DateTime = datetime.now().strftime('%Y-%m-%d/%H:%M:%S')

    g.db.execute('insert into boards (id, btype, ctype, subject, content, username, writedate, shared) values (?, ?, ?, ?, ?, ?, ?, ?)',
                 [session['id'], '-1', request.form['ctype'], request.form['subject'], request.form['content'], session['username'], DateTime, '0'])
    g.db.commit()

    return my_works()

@app.route('/my_work_execute', methods=['POST'])
def my_work_execute():
    if request.form['submit'] == 'remove':
        print(request.form)
        g.db.execute('delete from boards where subject = ? and username = ? and writedate = ? and ctype = ? and btype = ? ',
                           [request.form['subject'], request.form['username'], request.form['writedate'], request.form['ctype'], '-1'])
        g.db.commit()
    elif request.form['submit'] == 'achieve':
        g.db.execute('delete from boards where subject = ? and username = ? and writedate = ? and ctype = ? and btype = ?',
                           [request.form['subject'], request.form['username'], request.form['writedate'], request.form['ctype'], '-1'])
        g.db.commit()

        type = request.form['ctype']

        if type == 'todo':
            type = 'doing'
        elif type == 'doing':
            type = 'done'
        else:
            return my_works()

        g.db.execute('insert into boards (id, btype, ctype, subject, content, username, writedate, shared) values (?, ?, ?, ?, ?, ?, ?, ?)',
            [session['id'], '-1', type, request.form['subject'], request.form['content'], session['username'], request.form['writedate'], '0'])
        g.db.commit()
    elif request.form['submit'] == 'share':
        cur = g.db.execute('select no from teams where name= ?', [session['curteam']])
        row = cur.fetchall()

        if len(row) != 0:
            g.db.execute('update boards set shared = ? where subject = ? and username = ? and writedate = ? and ctype = ? and btype = ?',
                               ['1', request.form['subject'], request.form['username'], request.form['writedate'], request.form['ctype'], '-1'])
            g.db.commit()

            cur2 = g.db.execute('select * from boards where subject = ? and username = ? and writedate = ? and btype = ?',
                                [request.form['subject'], request.form['username'], request.form['writedate'], row[0][0]])
            row2 = cur.fetchall()

            if len(row2) == 0:
                g.db.execute('insert into boards (id, btype, ctype, subject, content, username, writedate, shared) values (?, ?, ?, ?, ?, ?, ?, ?)',
                [session['id'], row[0][0], request.form['ctype'], request.form['subject'], request.form['content'], session['username'], request.form['writedate'], '1'])

                g.db.commit()

    return my_works()

@app.route('/team_work_execute', methods=['POST'])
def team_work_execute():
    cur = g.db.execute('select no from teams where name= ?', [session['curteam']])
    row = cur.fetchall()
    print(row[0][0])
    if request.form['submit'] == 'remove':
        g.db.execute('delete from boards where subject = ? and username = ? and writedate = ? and ctype = ? and btype = ? ',
                           [request.form['subject'], request.form['username'], request.form['writedate'], request.form['ctype'], row[0][0]])
        g.db.commit()
    elif request.form['submit'] == 'achieve':
        g.db.execute('delete from boards where subject = ? and username = ? and writedate = ? and ctype = ? and btype = ?',
                           [request.form['subject'], request.form['username'], request.form['writedate'], request.form['ctype'], row[0][0]])
        g.db.commit()

        type = request.form['ctype']

        if type == 'todo':
            type = 'doing'
        elif type == 'doing':
            type = 'done'
        else:
            return team_works()

        g.db.execute('insert into boards (id, btype, ctype, subject, content, username, writedate, shared) values (?, ?, ?, ?, ?, ?, ?, ?)',
            [session['id'], row[0][0], type, request.form['subject'], request.form['content'], session['username'], request.form['writedate'], '1'])
        g.db.commit()

    return team_works()

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return render_template('dashboard.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0')
