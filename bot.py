# Add at the top
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# In main() function, add before application.run_polling():
threading.Thread(target=run_web).start()
