import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive and running via Webhook!"

def run():
    port = int(os.environ.get("PORT", 5000))  # Render يمرر PORT تلقائيًا
    app.run(host='0.0.0.0', port=port)
