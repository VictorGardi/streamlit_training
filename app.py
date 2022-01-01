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

def get_workout_locations(collection):
    locations = list()
    for doc in collection.stream():
        if doc.to_dict()['location'].lower() not in locations:
            locations.append(doc.to_dict()['location'].lower())
    return locations

def main():
    db = init_connection()
    collection = get_collection(db)
    choice = st.sidebar.selectbox('What do you want to do today?', ['Add workout', 'statistics'])
    if choice == 'Add workout':
        type_of_workout = st.selectbox('What type of workout did you do?', get_workout_choices(collection) + ['Other', 'Add new'])
        if type_of_workout != 'Add new':
            type_of_workout = st.text_input('Add new type of workout')
        location = st.selectbox('Where did you workout?', get_workout_locations(collection) + ['Add new'])
        if location != 'Add new':
            location = st.text_input('Add new location')
        
    else:
        pass

main()