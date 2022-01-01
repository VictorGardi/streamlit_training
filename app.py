import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

st.header('Hello 🌎!')
if st.button('Balloons?'):
    st.balloons()

import json
st.write(st.secrets)
key_dict = json.loads(st.secrets["textkey"])

# Use a service account
cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()

collection = doc_ref = db.collection("workouts")
for doc in collection.stream():
	st.write("The id is: ", doc.id)
	st.write("The contents are: ", doc.to_dict())