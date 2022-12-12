from snowflake.snowpark.session import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import *
import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt
from snowflake.snowpark.functions import udf
import datetime as dt
import numpy as np
import seaborn as sns
import dill
import random

# to divide train and test set
from sklearn.model_selection import train_test_split

# feature scaling
from sklearn.preprocessing import MinMaxScaler


from .config import snowflake_conn_prop
from snowflake.snowpark import version

sour_table_name = 'XURAN_TABLE'
dest_table_name = 'TABLE_ORIG'


def encode(s: str):
    if "None" in s:
        s = s.replace("None", " ")
    elif re.search(r'Ave[.]*$', s):
        s = s.replace("Ave", "Avenue")
    elif re.search(r'Av[.]*$', s):
        s = s.replace("Av", "Avenue")
    elif re.search(r'St[.]*$', s):
        s = s.replace("St", "Street")
    elif re.search(r'Rd[.]*$', s):
        s = s.replace("Rd", "Road")
    elif re.search(r'Dr[.]*$', s):
        s = s.replace('Dr', "Drive")
    return s


'''
register a new user with given info
use per-trained model
'''


def register(firstName, lastName, addressLine1, addressLine2, addressLine3, city, state, zipCode):
    session = Session.builder.configs(snowflake_conn_prop).create()
    print(session.sql(
        'select current_warehouse(), current_database(), current_schema()').collect())
    raw = session.table(dest_table_name)
    data = raw.toPandas().drop(columns=['P1_CONTACT_ID', 'P1_FIRSTNAME', 'P1_MIDDLENAME',
                                        'P1_LASTNAME', 'P1_ADDRESS_LINE_2', ], axis=5)
    data['P2_ADDRESS_LINE_1'] = [addressLine1 for i in range(len(data))]
    data['P2_ADDRESS_LINE_3'] = [addressLine3 for i in range(len(data))]
    data['P2_CITY'] = [city for i in range(len(data))]
    data['P2_STATE'] = [state for i in range(len(data))]
    data['P2_ZIP'] = [zipCode for i in range(len(data))]
    data["P2_ADDRESS_LINE_1"] = data.apply(lambda row: encode(
        str(row["P2_ADDRESS_LINE_1"])), axis=1).map(str)
    data["P2_ADDRESS_LINE_3"] = data.apply(lambda row: encode(
        str(row["P2_ADDRESS_LINE_3"])), axis=1).map(str)
    with open('./services/model.pkl', 'rb') as in_strm:
        model = dill.load(in_strm)
    
    pred = model.predict_proba(data)[:, 1]
    predictions = [round(value) for value in pred]
    if 0 not in predictions:
        noFamilyAssigned(firstName, lastName, addressLine1,
                         addressLine2, addressLine3, city, state, zipCode)
    else:
        familyAssigned(firstName, lastName, addressLine1, addressLine2,
                       addressLine3, city, state, zipCode, predictions.index(0))
    return 0


def familyAssigned(firstName, lastName, addressLine1, addressLine2, addressLine3, city, state, zipCode, index):
    session = Session.builder.configs(snowflake_conn_prop).create()
    raw = session.table(sour_table_name)
    data = raw.toPandas()

    contact_id = str(len(data)+1)
    full_name = firstName+' '+lastName
    session.sql('INSERT INTO ' + sour_table_name+' VALUES (' +
                contact_id+',\''+full_name+'\',\''+firstName+'\',\'\',\''+lastName+'\',\'' +
                addressLine1+'\',\''+addressLine2+'\',\''+addressLine3+'\',\'' +
                city+'\',\''+state+'\',\''+zipCode+'\',\''+data['HOUSEHOLD_ID'][index]+'\',\'Y\')').collect()

    session.sql('UPDATE ' + sour_table_name+' SET HOUSEHOLDED_IND=\'Y\' where CONTACT_ID=\'' +
                data['CONTACT_ID'][index]+'\'').collect()

    session.sql('INSERT INTO ' + dest_table_name+' VALUES (' +
                contact_id+',\''+firstName+'\',\'\',\''+lastName+'\',\'' +
                addressLine1+'\',\''+addressLine2+'\',\''+addressLine3+'\',\'' +
                city+'\',\''+state+'\',\''+zipCode+'\')').collect()

    return 0


def noFamilyAssigned(firstName, lastName, addressLine1, addressLine2, addressLine3, city, state, zipCode):
    session = Session.builder.configs(snowflake_conn_prop).create()
    raw = session.table(sour_table_name)
    data = raw.toPandas()
    x = str(random.randrange(10000000, 100000000))
    while x in data['HOUSEHOLD_ID']:
        x = str(random.randrange(10000000, 100000000))
    data['HOUSEHOLD_ID'][len(data)-1] = x

    contact_id = str(len(data)+1)
    full_name = firstName+' '+lastName
    session.sql('INSERT INTO ' + sour_table_name+' VALUES (' +
                contact_id+',\''+full_name+'\',\''+firstName+'\',\'\',\''+lastName+'\',\'' +
                addressLine1+'\',\''+addressLine2+'\',\''+addressLine3+'\',\'' +
                city+'\',\''+state+'\',\''+zipCode+'\',\''+x+'\',\'N\')').collect()

    session.sql('INSERT INTO ' + dest_table_name+' VALUES (' +
                contact_id+',\''+firstName+'\',\'\',\''+lastName+'\',\'' +
                addressLine1+'\',\''+addressLine2+'\',\''+addressLine3+'\',\'' +
                city+'\',\''+state+'\',\''+zipCode+'\')').collect()
    return 0


def remove(contact_ID):
    session = Session.builder.configs(snowflake_conn_prop).create()
    session.sql('DELETE FROM ' + sour_table_name +
                ' WHERE CONTACT_ID=\''+contact_ID+'\'').collect()

    session.sql('DELETE FROM ' + dest_table_name +
                ' WHERE P1_CONTACT_ID=\''+contact_ID+'\'').collect()

# helper method for remove to display table after removing user
def removeDisplay():
    # Create session,  get the source table(Xuran Table),  and return pandas df
    session = Session.builder.configs(snowflake_conn_prop).create()
    raw = session.table(sour_table_name)
    data=raw.toPandas()
    return(data)


def update(contact_ID, firstName, lastName, addressLine1, addressLine2, addressLine3, city, state, zipCode):
    session = Session.builder.configs(snowflake_conn_prop).create()
    full_name = firstName+' '+lastName
    session.sql('UPDATE ' + sour_table_name+' SET FULL_NAME=\'' +
                full_name+'\',FIRST_NAME=\''+firstName+'\',LAST_NAME=\''+lastName+'\',ADDRESS_LINE_1=\'' +
                addressLine1+'\',ADDRESS_LINE_2=\''+addressLine2+'\',ADDRESS_LINE_3=\''+addressLine3+'\',CITY=\'' +
                city+'\',STATE=\''+state+'\',ZIP=\''+zipCode+'\' WHERE CONTACT_ID=\''+contact_ID+'\'').collect()

    session.sql('UPDATE ' + dest_table_name+' SET P1_FIRSTNAME=\''+firstName+'\',P1_LASTNAME=\''+lastName+'\',P1_ADDRESS_LINE_1=\'' +
                addressLine1+'\',P1_ADDRESS_LINE_2=\''+addressLine2+'\',P1_ADDRESS_LINE_3=\''+addressLine3+'\',P1_CITY=\'' +
                city+'\',P1_STATE=\''+state+'\',P1_ZIP=\''+zipCode+'\' WHERE P1_CONTACT_ID=\''+contact_ID+'\'').collect()


def find(contact_ID):
    session = Session.builder.configs(snowflake_conn_prop).create()
    return [session.table(sour_table_name).toPandas()[str(int(contact_ID)-1)],
            session.table(dest_table_name).toPandas()[str(int(contact_ID)-1)]]


def addDashboardUser(firstName, lastName, addressLine1, addressLine2, addressLine3, city, state, zipCode):
    # 0 - no family
    # 1 - family
    predictionCode = register(firstName, lastName, addressLine1, addressLine2, addressLine3, city, state, zipCode)

    # Create session,  get the source table(Xuran Table),  and return pandas df
    session = Session.builder.configs(snowflake_conn_prop).create()
    raw = session.table(sour_table_name)
    data=raw.toPandas()
    return(data)

