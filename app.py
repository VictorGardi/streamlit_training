import json
from re import DEBUG
from altair.vegalite.v4.schema.channels import Tooltip
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import pandas as pd
import altair as alt

def init_connection():
    if not firebase_admin._apps:
        key_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()

def get_collection(db, collection='workouts'):
    return db.collection(collection)

def print_all_docs_in_collection(collection):
    for doc in collection.stream():
        st.write(doc.to_dict())

def firestore_to_pandas(collection):
    workouts = list(collection.stream())

    workouts_dict = list(map(lambda x: x.to_dict(), workouts))
    df = pd.DataFrame(workouts_dict)
    return df

def get_docs_between_dates(collection, start_date, end_date):
    return collection.where(u'timestamp', u'>=', start_date).where(u'timestamp', u'<', end_date).get()


def get_activity_choices(collection):
    activities = list()
    for doc in collection.stream():
        if doc.to_dict()['activity'] not in activities:
            activities.append(doc.to_dict()['activity'])
    return activities

def get_workout_choices(collection):
    workout_choices = list()
    for doc in collection.stream():
        if doc.to_dict()['type_of_workout'] not in workout_choices:
            workout_choices.append(doc.to_dict()['type_of_workout'])
    return workout_choices

def get_workout_locations(collection):
    locations = list()
    for doc in collection.stream():
        if doc.to_dict()['location'] not in locations:
            locations.append(doc.to_dict()['location'])
    return locations

def create_metric(collection):
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(days=7)
    two_weeks_ago = now - datetime.timedelta(days=14)
    number_of_workouts_last_week = len(get_docs_between_dates(collection, one_week_ago, now))
    number_of_workouts_two_weeks_ago = len(get_docs_between_dates(collection, two_weeks_ago, one_week_ago))
    delta = number_of_workouts_last_week - number_of_workouts_two_weeks_ago
    st.sidebar.metric('Number of workouts during the last seven days', value=number_of_workouts_last_week, delta=delta)

def main():
    db = init_connection()
    collection = get_collection(db)
    create_metric(collection)

    choice = st.sidebar.selectbox('What do you want to do today?', ['Add workout', 'History'])
    if choice == 'Add workout':
        st.header('Add workout')
        col1, col2 = st.columns(2)
        activity = col1.selectbox('What type of workout did you do?', get_activity_choices(collection) + ['Other', 'Add new'])
        if activity == 'Add new':
            activity = col1.text_input('Add new type of workout')

        type_of_workout = col1.selectbox('What type of workout did you do?', get_workout_choices(collection) + ['Other', 'Add new'])
        if type_of_workout == 'Add new':
            type_of_workout = col1.text_input('Add new type of workout')

        location = col2.selectbox('Where did you workout?', get_workout_locations(collection) + ['Add new'])
        if location == 'Add new':
            location = col2.text_input('Add new location')
        
        date = col1.date_input('At which date did you workout?')
        time = col2.time_input('At what time did you workout')
        timestamp = datetime.datetime.combine(date, time)

        duration = col1.number_input('What was the duration of the workout?', min_value=1, max_value=1000, value=60, help='Duration of workout in minutes')
        intensity = col2.number_input('How intense was the workout?', min_value=1, max_value=10, value=5)
        distance = col1.number_input('What was the distance of the workout?', min_value=0, help='Distance moved during workout in meters')
        doc = {
            "type_of_workout": type_of_workout,
            "location": location,
            "timestamp": timestamp,
            "intensity": intensity,
            "duration": duration,
            "distance": distance,
            "activity": activity
        }
        add_doc = st.button('Add workout')
        if add_doc:
            try:
                collection.add(doc)
                st.success('Succesfully added workout!')
            except Exception as e:
                st.exception(e)
            
    else:
        st.header('History')
        #print_all_docs_in_collection(collection)
        df = firestore_to_pandas(collection)
        df['date'] = df['timestamp'].dt.date
        #group_by_date = df.groupby(['date']).size()
        #group_by_date.reset_index()
        #group_by_date = group_by_date.to_frame(name='Number of workouts')
        #st.write(df)
        #st.write(group_by_date)
        #st.bar_chart(group_by_date)
        #temp = df.groupby(['date', 'activity'])
        #st.write(temp)
        #temp = temp.unstack(level=-1)
        #temp.fillna(0, inplace=True)
        df['Number of workouts'] = 1

        c = alt.Chart(df).mark_bar().encode(
            x='date:T',
            y='duration:Q',
            color='activity',
            tooltip=['type_of_workout', 'distance', 'intensity', 'location']
            )

        #st.altair_chart(c, use_container_width=True)
        st.altair_chart(c, use_container_width=True)

main()