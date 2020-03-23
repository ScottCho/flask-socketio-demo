from flask import Flask, render_template
from flask_socketio import SocketIO,emit
import subprocess
from threading import Lock
import random
import eventlet


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

thread = None
thread_lock = Lock()

def ack():
    print('message was received!')

@app.route('/')
def index():
        return render_template('index.html')

#处理接收到的客户端信息
@socketio.on('connect event',namespace='/task')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    emit('event2',str(json),namespace='/task',callback=ack)

@socketio.on('event2',namespace='/task')
def background_task():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

def background_thread():
    p = subprocess.Popen('ping qq.com',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while True:
        line = p.stdout.readline().strip()
        line=line.decode(encoding='utf-8')
        #line = random.randint(1, 100)
        print('line='+line)
        if line:
            socketio.sleep(2)
            socketio.emit('event2', line,namespace='/task')
            

@app.route('/task')
def start_background_task():
    background_task()
    return 'Started'

if __name__ == '__main__':
        socketio.run(app,host='0.0.0.0', port=5001)
