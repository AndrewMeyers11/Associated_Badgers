from flask import Flask, request, render_template, redirect, url_for
import logging
import sys
from services import register
import pandas as pd
import dataframe_image as dfi


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['POST', 'GET'])
def home():

    updatedDf = pd.DataFrame()

    # Add Info button clicked
    if request.method == 'POST':

        # if request.form['submit_button'] == "Add":

        # Get user one input
        userOneFName = request.form['userOneFName']
        userOneLName = request.form['userOneLName']
        userOneStreet = request.form['userOneStreet']
        userOneApt = request.form['userOneApt']
        userOneCity = request.form['userOneCity']
        userOneState = request.form['userOneState']
        userOneZip = request.form['userOneZip']

        # Check validity of the input for user one, redirect to err if faulty
        if not userOneFName or not userOneLName or not userOneStreet or not userOneCity or not userOneState or not userOneZip:
            return redirect(url_for('inputInvalid'))

        # Check if second user is specified
        secUserChecked = request.form['secondUser']

        # Get user Two Input
        if secUserChecked == 'Yes':
            userTwoFName = request.form['userTwoFName']
            userTwoLName = request.form['userTwoLName']
            userTwoStreet = request.form['userTwoStreet']
            userTwoApt = request.form['userTwoApt']
            userTwoCity = request.form['userTwoCity']
            userTwoState = request.form['userTwoState']
            userTwoZip = request.form['userTwoZip']

            # Check validity of the input for user two, redirect to err if faulty
            if not userTwoFName or not userTwoLName or not userTwoStreet or not userTwoCity or not userTwoState or not userTwoZip:
                return redirect(url_for('inputInvalid'))

        # Run first User through the model
        updatedDf = register.addDashboardUser(userOneFName, userOneLName, userOneStreet, userOneApt, (userOneCity +
                                                                                                      ' ' + userOneState + ' ' + userOneZip), userOneCity, userOneState, userOneZip)

        # Run second user through the model(if applicable)
        if secUserChecked == 'Yes':
            updatedDf = register.addDashboardUser(userTwoFName, userTwoLName, userTwoStreet, userTwoApt, (userTwoCity +
                                                                                                          ' ' + userTwoState + ' ' + userTwoZip), userTwoCity, userTwoState, userTwoZip)
        return render_template('index.html', DATA_FRAME_OUTPUT = updatedDf.to_html())

        # if request.form['submit_button'] == "Remove":
        #     # insert remove code here
        #     # only need contact_id to remove user not sure how we want to display that
        #     pass

        # if request.form['submit_button'] == "Lookup":
        #     # insert lookup code here
        #     # only need contact_id to find user as well
        #     pass

    else:
        return render_template('index.html', DATA_FRAME_OUTPUT = updatedDf.to_html())


@app.route('/invalid-input', methods=['GET'])
def inputInvalid():
    return "INVALID INPUT, THROW ERROR CODE 422"


@app.route('/remove.html', methods=['POST', 'GET'])
def remove():
    newdf = pd.DataFrame()
    if request.method == 'POST':
        userContactID = request.form['usercontactID']

        if not userContactID:
            return redirect(url_for('inputInvalid'))

        register.remove(userContactID)
        newdf = register.removeDisplay()
        return render_template('index.html', DATA_FRAME_OUTPUT = newdf.to_html())


    if request.method == 'GET':
        if request.path == '/remove.html':
            with open("./templates/remove.html") as f:
                html = f.read()
            return html
        
         


@app.route('/lookup.html', methods=['POST', 'GET'])
def lookup():
    newdf = pd.DataFrame()
    if request.method == 'POST':
        userContactID = request.form['usercontactID']

        if not userContactID:
            return redirect(url_for('inputInvalid'))

        newdf = register.find(userContactID)
        return render_template('index.html', DATA_FRAME_OUTPUT = newdf.to_html())

    if request.method == 'GET':
        if request.path == '/lookup.html':
            with open("./templates/lookup.html") as f:
                html = f.read()
            return html


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)


# ------------------------------------------------------------
# To run the app:
#   python3 application.py (runs continuously until you kill w/ ctrl+C)
#   http://<YOUR_IP or localhost>:5000
#
#   NOTE: You need to be running python 3.8.  You should make a virtual environment that uses python 3.8 and then use pip to install all of the necessary packages
#           This requirement comes from SnowPark
