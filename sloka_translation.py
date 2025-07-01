import streamlit as st
from googletrans import Translator
from gtts import gTTS                   
import os                                   
                         
# Language map for translation + TTS
language_map = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn"
}

translator = Translator()

# Streamlit UI
st.set_page_config(page_title="Sloka Translator + Audio", layout="centered")
st.title("🕉️ Sloka Translator + Explanation + Audio")
st.markdown("Enter a sloka in any language and get pronunciation and meaning separately in audio.")

# User input
sloka = st.text_area("📜 Enter the Sloka here:", height=150)
target_lang = st.selectbox("🌍 Translate To", list(language_map.keys()))
lang_code = language_map[target_lang]

# Translation and audio generation
if st.button("🔁 Translate, Pronounce & Explain"):
    if not sloka.strip():
        st.warning("⚠️ Please enter a sloka.")
    else:
        try:
            # 🌐 Translate the sloka
            translation = translator.translate(sloka, dest=lang_code)
            translated_text = translation.text

            # 📖 Display translation
            st.subheader("📖 Translated Sloka")
            st.write(translated_text)

            # 🎤 Generate pronunciation audio (Sloka in original style)
            tts_sloka = gTTS(text=sloka, lang="hi")  # For Sanskrit-style pronunciation
            sloka_audio_path = "sloka_pronunciation.mp3"
            tts_sloka.save(sloka_audio_path)

            # 🎤 Generate explanation audio (Meaning in selected language)
            tts_explanation = gTTS(text=translated_text, lang=lang_code)
            explanation_audio_path = "sloka_meaning.mp3"
            tts_explanation.save(explanation_audio_path)

            # 🎧 Separate players
            st.subheader("🔊 Sloka Pronunciation")
            st.audio(sloka_audio_path)

            st.subheader("🧠 Meaning / Explanation")
            st.audio(explanation_audio_path)

        except Exception as e:
            st.error(f"❌ Error: {e}")