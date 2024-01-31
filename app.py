import os
import time
import wave
import pyaudio
import threading
import speech_recognition as sr
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
#from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy
from text_summ import abs_summ
from twilio.rest import Client
import random
app = Flask(__name__)
app.secret_key = '@890kkkd45?!890'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
db = SQLAlchemy(app)

@app.route('/')
def page1():
    return render_template('page1.html')


# Twilio credentials
account_sid = 'AC1499bc5499890e70897a2c325edafcc9'
auth_token = '1041846420e33d21a77df004b0982e3c'
twilio_phone_number = +17652123855

#@app.route('/')
#def index():
#    return render_template('index.html')

# Generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Store the OTP for verification later
otp_storage = {}

# Route to send OTP to the mobile number
@app.route('/send-otp', methods=['POST'])
def send_otp():
    global mobilenumber
    global username
    global password
    mobilenumber = request.form.get('mobilenumber')
    username = request.form.get('username')
    password = request.form.get('password')

    if not mobilenumber:
        return "Mobile number is required", 400

    # Generate OTP
    otp = generate_otp()

    # Store the OTP
    otp_storage[mobilenumber] = otp

    # Send the OTP via Twilio
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f'Your OTP is: {otp}',
        from_=twilio_phone_number,
        to=mobilenumber
    )
    return render_template('verifyOtp.html')
# Route to verify the OTP
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    #mobile_number = request.form.get('mobile_number')
    user_entered_otp = request.form.get('otp')

    #if not mobile_number or not user_entered_otp:
    if not user_entered_otp:
        return "Mobile number and OTP are required", 400

    # Retrieve the stored OTP
    stored_otp = otp_storage.get(mobilenumber)

    if stored_otp == user_entered_otp:
        #return "OTP verification successful"
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html',error_message="Username already exists. Please choose a different username.")
        # Create a new user and add it to the database
        new_user = User(username=username, password=password,mobilenumber=mobilenumber)
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
        # return redirect(url_for('loginK'))
        return render_template('loginK.html',error_message="User registered successfully. Please login to proceed.")

        #return redirect('/register')
    else:
        return "Invalid OTP", 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error_message="Username already exists. Please choose a different username.")
        # Create a new user and add it to the database
        new_user = User(username=username, password=password)#,mobilenumber=mobilenumber)
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
        #return redirect(url_for('loginK'))
        return render_template('loginK.html', error_message="Username registered successfully. Please login to proceed.")

    return render_template('register.html')

# Route for login
@app.route('/loginK', methods=['GET', 'POST'])
def loginK():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('loginK.html',error_message="Username invalid. Please register.")

        if user and user.password == password:
            session['username'] = user.username  # Store the username in the session
            session['user_id'] = user.id
            return render_template('index.html')
        else:
            #return render_template('register.html')
            return "please register first"

    return render_template('loginK.html')



@app.route('/index')
def index():
    return render_template('index.html')
# Define a User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    mobilenumber = db.Column(db.String(13), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    text_to_summarize = db.Column(db.Text, nullable=False)
    generated_summary = db.Column(db.Text, nullable=False)
def create_tables():
    with app.app_context():
        db.create_all()
# Call the create_tables() function to create the tables within the Flask context
create_tables()
@app.route('/save_summary', methods=['POST','GET'])
def save_summary():
    user_id = session['user_id']  # Assuming you're using Flask-Login for authentication
    text_to_summarize = request.form.get('rawtext')
    abs_result=abs_summ(text_to_summarize)
    generated_summary = abs_result[1]  # Replace with your logic
    summary = Summary(user_id=user_id, text_to_summarize=text_to_summarize, generated_summary=generated_summary)
    db.session.add(summary)
    db.session.commit()
    return 'Summary saved successfully'

@app.route('/a', methods=['GET', 'POST'])
def a():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        generated_summary, text_to_summarize, len_of_txt, len_of_smry = abs_summ(rawtext)

    user_id = session['user_id']  # Assuming you're using Flask-Login for authentication
    #text_to_summarize = request.form.get('rawtext')
    #abs_result = abs_summ(text_to_summarize)
    #generated_summary = abs_result[1]  # Replace with your logic

    summary = Summary(user_id=user_id, text_to_summarize=text_to_summarize, generated_summary=generated_summary)
    db.session.add(summary)
    db.session.commit()
    #return 'Summary saved successfully'
    return render_template('a.html', summary=generated_summary, original_text=text_to_summarize, len_of_txt=len_of_txt, len_of_smry=len_of_smry)

@app.route('/history')
def list_users():
    user_id = session['user_id']
    user = User.query.filter_by(id=user_id)
    summary = Summary.query.filter_by(user_id=user_id)
    return render_template('history.html', users=user,summary=summary)

output_folder = "recorded audio"
os.makedirs(output_folder,exist_ok=True)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

audio=pyaudio.PyAudio()
frames=[]
recording=False
recording_thread=None

def record():
    global frames
    global recording
    recording=True
    stream=audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=0
    )
    frames=[]
    while recording:
        data=stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()


@app.route("/logout")
def logout():
    session.pop('username', None)
    #session.pop('email', None)
    session.pop('user_id', None)
    session.clear()
    #return redirect(url_for("index"))
    return redirect("/")

# ... (other routes and code)
@app.route('/start_recording',methods=['POST'])
def start_recording():
    global recording
    global recording_thread
    recording=True
    recording_thread=threading.Thread(target=record)
    recording_thread.start()
    return redirect(url_for('index'))

@app.route('/stop_recording',methods=['POST'])
def stop_recording():
    global recording
    global recording_thread
    recording=False
    recording_thread.join()

    timestamp=int(time.time())
    output_filename=os.path.join(output_folder,f"audio_{timestamp}.wav")

    with wave.open(output_filename,"wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

        recognizer = sr.Recognizer()
        with sr.AudioFile(output_filename) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            return jsonify({'text_result': text})
        except sr.UnknownValueError:
            return jsonify({'text_result': "Could not understand the audio"})
    """ except sr.RequestError as e:
            return jsonify({'text_result': f"Could not request results;{e}"})
    """
    #return render_template('index.html',audio_saved=output_filename)

if __name__=="__main__":
    app.run(debug=True)