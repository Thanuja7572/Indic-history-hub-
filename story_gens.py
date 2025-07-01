import streamlit as st
import requests
from urllib.parse import quote
import re

# Configure the app
st.set_page_config(
    page_title="✨ Magic Indian Stories",
    layout="centered",
    page_icon="📚"
)

# Custom CSS for visual enhancements
st.markdown("""
    <style>
        body {
            background-color: #fef6f0;
        }
        .title {
            font-size: 38px;
            font-weight: bold;
            color: #4a2c2a;
            text-align: center;
        }
        .subtext {
            font-size: 18px;
            color: #5a3e36;
            text-align: center;
            margin-bottom: 20px;
        }
        .story-box {
            background: #fff9f0;
            padding: 30px;
            border-radius: 20px;
            font-size: 18px;
            line-height: 1.7;
            color: black;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        }
        .footer {
            font-size: 14px;
            text-align: center;
            color: gray;
            margin-top: 50px;
        }
    </style>
""", unsafe_allow_html=True)

# API Configuration
WIKI_API = "https://{lang}.wikipedia.org/w/api.php"
WIKI_REST = "https://{lang}.wikipedia.org/api/rest_v1"

# Story Database
STORY_DB = {
    'Kings & Queens': [
        ('Krishnadevaraya', 'Vijayanagara king'),
        ('Rani Lakshmibai', 'Queen of Jhansi'),
        ('Raja Raja Chola', 'Great Chola emperor')
    ],
    'Freedom Fighters': [
        ('Subhas Chandra Bose', 'Netaji'),
        ('Bhagat Singh', 'Revolutionary'),
        ('Sarojini Naidu', 'Poet and activist')
    ],
    'Scientists & Scholars': [
        ('Aryabhata', 'Ancient mathematician'),
        ('C. V. Raman', 'Nobel Prize physicist'),
        ('Sushruta', 'Ancient surgeon')
    ]
}

LANGUAGES = {
    'English': 'en',
    'Hindi': 'hi',
    'Telugu': 'te',
    'Tamil': 'ta',
    'Bengali': 'bn'
}

AGE_CONFIG = {
    '5-8 years': {'max_words': 800, 'font': 20},
    '9-12 years': {'max_words': 2000, 'font': 18},
    '13+ years': {'max_words': 4000, 'font': 16}
}

# Utility Functions
def fetch_wiki_content(title, lang='en'):
    try:
        search_url = WIKI_API.format(lang=lang) + f"?action=query&list=search&srsearch={quote(title)}&format=json"
        search_res = requests.get(search_url, timeout=5)
        if search_res.status_code != 200 or not search_res.json().get('query', {}).get('search'):
            return None
        page_title = search_res.json()['query']['search'][0]['title']
        content_url = WIKI_REST.format(lang=lang) + f"/page/summary/{quote(page_title)}"
        content_res = requests.get(content_url, timeout=5)
        if content_res.status_code == 200:
            return content_res.json().get('extract')
    except requests.exceptions.RequestException:
        return None
    return None

def clean_content(text):
    if not text:
        return ""
    text = re.sub(r'\[[0-9]+\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_story(content, character, char_type, age_group):
    if not content:
        return None
    words = content.split()
    max_words = AGE_CONFIG[age_group]['max_words']
    truncated = ' '.join(words[:max_words])
    story = f"""
    🌟 **The Amazing Story of {character} ({char_type})** 🌟

    Long ago in India...

    {truncated}

    And that's how {character} became legendary in Indian history!
    """
    return clean_content(story)

# --- UI Layout ---
st.markdown('<div class="title">📖 Magic Indian Stories for Kids</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Stories from history brought to life with Wikipedia!</div>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        age = st.selectbox('👶 Choose Age Group', options=list(AGE_CONFIG.keys()))
    with col2:
        language = st.selectbox('🌐 Select Language', options=list(LANGUAGES.keys()))

category = st.selectbox('🏰 Story Category', options=list(STORY_DB.keys()))
character, char_type = st.selectbox('🎯 Choose a Historical Figure', options=STORY_DB[category])

# Button to Generate Story
if st.button('✨ Create Magic Story', type='primary'):
    with st.spinner('🪄 Generating your story...'):
        lang_code = LANGUAGES[language]
        content = fetch_wiki_content(character, lang_code)

        if not content and language != 'English':
            st.warning(f"⚠️ Couldn’t find it in {language}. Trying English version...")
            content = fetch_wiki_content(character, 'en')

        if not content:
            st.error(f"""
            ❌ Couldn't find this story. Try:
            1. Switching to English  
            2. Choosing a different character  
            3. Checking spelling on Wikipedia
            """)
        else:
            story = format_story(content, character, char_type, age)

            # Audio
            audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={quote(story)}&tl={lang_code}&client=tw-ob"
            st.audio(audio_url, format='audio/mp3')

            # Story Box
            st.markdown(f'<div class="story-box">{story}</div>', unsafe_allow_html=True)

            # Optional Image
            try:
                img_url = WIKI_REST.format(lang=lang_code) + f"/page/media/{quote(character)}"
                img_data = requests.get(img_url).json()
                if img_data.get('items'):
                    st.image(img_data['items'][0]['srcset'][0]['src'], caption=f"Image of {character}")
            except:
                pass

# Footer
st.markdown('<div class="footer">📚 All stories sourced from Wikipedia. For educational purposes only.</div>', unsafe_allow_html=True)
