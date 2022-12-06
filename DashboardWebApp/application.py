from flask import Flask
import logging
import sys

app = Flask(__name__)

logging.basicConfig(level = logging.DEBUG)

@app.route('/')
def home():
    # Debugging reference notes
    # app.logger.warning('testing warning log')
    # app.logger.error('testing error log')
    # app.logger.info('testing info log')
    # return "Check your console"
    
    with open("./templates/index.html") as f:
        html = f.read()
    return html

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True)

    
    
# ------------------------------------------------------------
# To run the app:
#   python3 application.py (will run until you kill w/ ctrl+C)
#   http://<YOUR_IP or localhost>:5000