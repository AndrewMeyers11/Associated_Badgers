from flask import Flask, request, render_template, redirect, url_for
import logging
import sys


app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['POST', 'GET'])
def home():
    # Debugging reference notes
    # app.logger.warning('testing warning log')
    # app.logger.error('testing error log')
    # app.logger.info('testing info log')
    # return "Check your console"

    # Add Info button clicked
    if request.method == 'POST':

        # Get user one input
        userOneFName = request.form['userOneFName']
        userOneLName = request.form['userOneLName']
        userOneAddr = request.form['userOneAddr']
        userOneState = request.form['userOneState']
        userOneZip = request.form['userOneZip']

        # Check validity of the input for user one, redirect to err if faulty
        if not userOneFName or not userOneLName or not userOneAddr or not userOneState or not userOneZip:
            return redirect(url_for('inputInvalid'))

        # Check if second user is specified
        secUserChecked = request.form['secondUser']

        # Get user Two Input
        if secUserChecked == 'Yes':
            userTwoFName = request.form['userTwoFName']
            userTwoLName = request.form['userTwoLName']
            userTwoAddr = request.form['userTwoAddr']
            userTwoState = request.form['userTwoState']
            userTwoZip = request.form['userTwoZip']

            # Check validity of the input for user two, redirect to err if faulty
            if not userTwoFName or not userTwoLName or not userTwoAddr or not userTwoState or not userTwoZip:
                return redirect(url_for('inputInvalid'))

        # run the model
        # Redirect to results page
        return 'run the model'

    elif request.method == 'GET':
        with open("./templates/index.html") as f:
            html = f.read()
        return html


@app.route('/invalid-input', methods=['GET'])
def inputInvalid():
    return "INVALID INPUT, THROW ERROR CODE 422"


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)


# ------------------------------------------------------------
# To run the app:
#   python3 application.py (runs continuously until you kill w/ ctrl+C)
#   http://<YOUR_IP or localhost>:5000
