from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running via Webhook!"

def run():
    app.run(host='0.0.0.0', port=5000)

