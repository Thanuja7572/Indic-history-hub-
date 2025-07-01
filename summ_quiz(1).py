import streamlit as st
from googletrans import Translator
from gtts import gTTS
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import tempfile
import os
import random
import re

translator = Translator()

# ✅ Safe translation
def safe_translate(text, dest_lang):
    try:
        result = translator.translate(text, dest=dest_lang)
        return result.text if result else text
    except:
        return text

# Supported languages
LANGUAGES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn"
}

st.set_page_config(page_title="MultiLang Summary & Quiz", layout="centered")
st.title("🌐 Multilingual Summary & Quiz Generator")

# Light cream background
st.markdown("""
    <style>
        body { background-color: #fffaf0; }
        .stApp { background-color: #fffaf0; }
    </style>
    """, unsafe_allow_html=True)

# Score storage
if "user_scores" not in st.session_state:
    st.session_state.user_scores = {}

# UI inputs
language = st.selectbox("🌐 Choose Language", list(LANGUAGES.keys()))
lang_code = LANGUAGES[language]
topic = st.text_input("🔍 Enter a topic (e.g., Pen, Lotus, Nike)")

if topic:
    try:
        search_results = wikipedia.search(topic)
        if not search_results:
            raise Exception("No Wikipedia articles found for this topic.")
        
        selected_title = st.selectbox("🔎 Did you mean:", search_results)

        try:
            page = wikipedia.page(selected_title, auto_suggest=False)
            summary_en = page.summary
        except DisambiguationError as e:
            st.error("Still ambiguous! Try selecting a more specific option.")
            st.stop()
        except PageError:
            st.error("Couldn't fetch the page. Please try another topic.")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.stop()

        translated_summary = safe_translate(summary_en, lang_code)
        st.subheader("📖 Summary")
        st.write(translated_summary)

        # Audio generation
        try:
            tts = gTTS(text=translated_summary, lang=lang_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name)
        except Exception as audio_err:
            st.warning(f"Audio error: {audio_err}")

        if st.button("Next ➡️ Start Quiz"):
            sentences = summary_en.split(". ")
            quiz = []

            for i in range(min(3, len(sentences))):
                sent = sentences[i]
                sent_clean = re.sub(r'\([^)]*\)', '', sent)
                words = [w for w in sent_clean.split() if w.istitle() and len(w) > 3]
                if not words:
                    words = [w for w in sent_clean.split() if len(w) > 5]

                keyword = random.choice(words) if words else topic
                question_en = f"What is '{keyword}' related to in the context?"
                correct_en = sent_clean.strip()
                wrongs = random.sample(
                    [s for s in sentences if s != sent], min(3, len(sentences)-1)
                )
                options_en = [correct_en] + [w.strip() for w in wrongs]
                random.shuffle(options_en)

                question_trans = safe_translate(question_en, lang_code)
                options_trans = [safe_translate(opt, lang_code) for opt in options_en]
                correct_trans = safe_translate(correct_en, lang_code)
                explanation_trans = correct_trans

                quiz.append({
                    "q": question_trans,
                    "options": options_trans,
                    "options_en": options_en,  # original for matching
                    "answer_en": correct_en,
                    "answer_trans": correct_trans,
                    "explanation": explanation_trans
                })

            st.session_state.quiz = quiz
            st.session_state.q_num = 0
            st.session_state.score = 0
            st.session_state.in_quiz = True
            st.session_state.topic = topic
            st.session_state.lang = language
            st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ✅ Quiz Display
if st.session_state.get("in_quiz", False):
    quiz = st.session_state.quiz
    qn = st.session_state.q_num

    if qn < len(quiz):
        q_data = quiz[qn]
        st.subheader(f"❓ Question {qn + 1}")
        st.write(q_data["q"])
        selected = st.radio("Choose an option:", q_data["options"], key=f"q{qn}")

        if st.button("Submit Answer"):
            correct_index = q_data["options_en"].index(q_data["answer_en"])
            correct_trans = q_data["options"][correct_index]

            if selected == correct_trans:
                st.success("✅ Correct!")
                st.markdown(f"**Explanation:** _{q_data['explanation']}_")
                st.session_state.score += 1
            else:
                st.error("❌ Incorrect.")
                st.markdown(f"**Correct Answer:** `{correct_trans}`")
                st.markdown(f"**Explanation:** _{q_data['explanation']}_")
            st.session_state.q_num += 1
            st.rerun()
    else:
        score = st.session_state.score
        st.success(f"🎉 Quiz Completed! Your score: {score}/3")

        topic = st.session_state.topic
        if topic not in st.session_state.user_scores:
            st.session_state.user_scores[topic] = []
        st.session_state.user_scores[topic].append(score)

        if st.button("🔁 Try Another Topic"):
            for k in ["quiz", "score", "q_num", "in_quiz", "topic", "lang"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

# ✅ Score History
if st.checkbox("📊 Show Score History"):
    scores = st.session_state.user_scores
    if scores:
        for i, (topic, score_list) in enumerate(scores.items(), 1):
            for s in score_list:
                st.write(f"**{i}.** *{topic}* — 🏆 Score: **{s}/3**")
    else:
        st.info("No quiz history found.")
