'''"Python Live Chat App."

Note:
1. Entering and leaving the chatroom will not be saved in the database
2. If there are no users left in a room, the room will be deleted, but the chat history will still be retained in the database.

Also don't forget to check "https://github.com/haddockam/Python-Live-Chat-App" for Acknowledgments and Known Issues
'''

# ----------------<required libraries>------------------
from flask import Flask, render_template, url_for, redirect, request, session
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import random
# ----------------<modify modules>------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some-secretkey' # enter your secret key!
socketio = SocketIO(app)
app.permanent_session_lifetime = timedelta(days=1) # keep session for 1 day
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # saves the database in this file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#-----------------------<class to modify database>-----------------------
class room_database(db.Model):
    __tablename__ = 'room_code'

    _id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100))
    user = db.Column(db.String(100))
    messages = db.Column(db.String(250))

    def __init__(self,code, user, messages):
        self.code = code
        self.user = user
        self.messages = messages

        messages = []

# ----------------<function to generate unique code>------------------
numbers = ['1','2','3','4','5','6','7','8','9'] # room code could include letters
rooms = {} # dictionary for room codes, and messages

def generate_code(length): # obviously generating unique code for room
    while True:
        code = ''
        for _ in range(length):
            code += random.choice(numbers)

        if code not in rooms: # will repeat if the room code exist
            break
    return code
# ----------------<the home page>------------------
@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        name = request.form.get('name') # getting user information and choices:
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)
        
        if not name: # handling errors:
            return render_template('home.html', error='PLease enter name', name=name, code=code)
        if join != False and not code:
            return render_template('home.html', error='PLease enter room code', name=name, code=code)
        
        room = code 
        if create != False: # if user pressed 'create room' on home page
            room = generate_code(4) 
            rooms[room] = {'members': 0, 'messages': []}
        elif code not in rooms:
                return render_template('home.html', error="Room doesn't exist", code=code, name=name)
        
        session['room'] = room # keep information in session
        session['name'] = name 

        new_user = room_database(room, name, '') # get information in database
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('chat_room')) # if everything went fine, goes to chat room

    return render_template('home.html') # if method != 'POST'
# -----------------<the chat room>-----------------
@app.route('/chat-room', methods=['POST','GET']) 
def chat_room():
    if request.method == 'GET': # if user just wants to chat (method == 'GET)
        room = session.get('room')
        if room is None or session.get('room') is None or room not in rooms: # handling errors
            return redirect(url_for('home'))

        return render_template('chat-room.html', room_code=room, messages=rooms[room]['messages'])
    
    if request.method == 'POST': # if user pressed a button
        user_logout = request.form.get('logout', False) # getting user choice
        if user_logout != False:
            return redirect(url_for('home'))
        else: # just in case the code crashed!!!
            return redirect(url_for('home'))
# ------------------<sending messages to chatroom>----------------
@socketio.on('message')
def message(data):
    name = session.get('name')
    room = session.get('room')
    if room not in rooms: # make sure room exist
        return
    
    content = { # making user's message prepared
        'name': session.get('name'),
        'message': data['data']
    }

    msg = content['message']
    new_msg = room_database(room, name, msg) # store messages in database
    db.session.add(new_msg)
    db.session.commit()

    send(content, to=room) # sending the information
    rooms[room]['messages'].append(content) # saving the information
# -------------------<connect users to chatroom>---------------
@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    if not room or not name: # handling errors
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)

    send({'name':name, 'message':'has entered the room'}, to=room,)
    
    rooms[room]['members'] += 1 # keep track of number of users
# ------------------<disconnect users from chatroom>----------------
@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)

    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0: # (if only one person remains, refreshing the page will automatically opt you out)
            del rooms[room] # deletes the room  if room is empty

    send({'name':name, 'message':'has left the room'}, to=room)
# ------------------<database page>----------------
@app.route('/show', methods=['POST','GET'])
def show():
    if request.method == 'POST':
        filter_room = request.form.get('filter') # filter the database for user

        del_room = request.form.get('filter_del') # room input to delete
        room_to_del = room_database.query.filter_by(code=del_room).all() # find room in database
        if room_to_del:
            for item in room_to_del:
                db.session.delete(item) # delete if existed
                db.session.commit()

        return render_template('show.html', values=room_database.query.all(), room_filter=filter_room)
    else:
        return render_template('show.html', values=room_database.query.all())
# -------------------<Have Fun!>---------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=65432, debug=True) # Don't forget to change host