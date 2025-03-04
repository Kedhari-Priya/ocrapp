import os
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import pytesseract
from PIL import Image
from googletrans import Translator
from gtts import gTTS
import google.generativeai as genai
import subprocess
import os
import time

# ✅ Initialize Firebase (Ensure the JSON file is uploaded to the project)
if not firebase_admin._apps:
    cred = credentials.Certificate("finalproject1411-firebase-adminsdk-fbsvc-f119f38ed7.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ✅ Configure Gemini API
genai.configure(api_key="AIzaSyD2H6p-rJU-uh0hVleY2VQb4Q2ZdJNl0HQ")  # Replace with your actual API key

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# ✅ Streamlit UI
st.title("OCR and Translation App")
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

languages = {"Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Urdu": "ur"}
selected_language = st.selectbox("Select translation language", list(languages.keys()))

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # ✅ OCR Processing
    extracted_text = pytesseract.image_to_string(image)

    # ✅ Translation
    translator = Translator()
    translated_text = translator.translate(extracted_text, dest=languages[selected_language]).text
    st.write("### Translated Text:", translated_text)

    # ✅ Text-to-Speech
    tts = gTTS(translated_text, lang=languages[selected_language])
    audio_path = "translated_audio.mp3"
    tts.save(audio_path)
    st.audio(audio_path, format="audio/mp3")

    # ✅ Chatbot Mode
    st.write("### Chatbot Mode: Ask questions about the image")
    user_query = st.text_input("Ask a question:")

    if user_query:
        db.collection("user_queries").add({"query": user_query})  # Store query in Firestore

        chat_session = model.start_chat(
            history=[{"role": "user", "parts": [
                f"Based on the following document text, answer the user's query. Document: {extracted_text}\nQuery: {user_query}"
            ]}]
        )
        response = chat_session.send_message(user_query)
        st.write("#### Answer:", response.text.strip())

# ✅ Run Streamlit
if __name__ == "__main__":
    st.write("App is running...")
