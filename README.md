# Python Live Chat App

This is a live chatting program written in Python using Flask, Flask-SQLAlchemy, and SocketIO.

## Features
- Allows users to chat with each other within the local network
- Real-time messaging using SocketIO
- Message history saving with Flask-SQLAlchemy

## Prerequisites
- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-SocketIO

## Installation
1. Clone the repository
2. Install the required dependencies using `pip install -r requirements.txt`
3. Run the application using `python main.py`
4. In the "socketio.run()" function, located on the last line of code, please input your host (e.g., 127.0.0.1 or 192.168.x.x) and your port number as well.
5. Access the application in your web browser at `http://Host:Port`

## Usage
1. Login to start chatting with other users in the local network
2. Send and receive messages in real-time
3. View message history and previous conversations

## Known Issues
- Deleting history from the show.html page deletes rooms but does not remove the related data from the "database.db" file.

## Acknowledgments
- it's recommended to use a port number that is not already in use by another application (e.g., 65432)
- The original idea was inspired by [techwithtim](https://github.com/techwithtim), I have enhanced it with CSS styling, setting up the database and creating a history page.
- The user icon displayed on the home page was sourced from [icons8](https://icons8.com/icons)
- If you have any suggestions, feel free to share them
