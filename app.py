import json
from re import DEBUG
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

st.header('Workouts')

def init_connection():
    if not firebase_admin._apps:
        key_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()

def get_collection(db, collection='workouts'):
    return db.collection(collection)

def add_doc_to_collection(collection, doc):
    pass

def get_workout_choices(collection):
    workout_choices = list()
    for doc in collection.stream():
        if doc.to_dict()['type_of_workout'].lower() not in workout_choices:
            workout_choices.append(doc.to_dict()['type_of_workout'].lower())
    return workout_choices

def main():
    db = init_connection()
    collection = get_collection(db)
    choice = st.sidebar.selectbox('What do you want to do today?', ['Add workout', 'statistics'])
    if choice == 'Add workout':
        workout_choices = get_workout_choices(collection)
        type_of_workout = st.selectbox('What type of workout did you do?', workout_choices + ['Other', 'Add new'])
        if type_of_workout != 'Add new':
            pass
    else:
        pass

""" for doc in collection.stream():
	st.write("The id is: ", doc.id)
	st.write("The contents are: ", doc.to_dict()) """

main()