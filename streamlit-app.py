import streamlit as st
import base64
import json
import pandas as pd
import time
import os


# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Voterastics 2025 - Live Count",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
# --- 2. FUNGSI LOAD DATA & GAMBAR ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')
    return df

# --- 3. CUSTOM CSS (MODIFIKASI DI SINI) ---

bg_file = "background2.png" 

try:
    bin_str = get_base64(bg_file)
    bg_css = f"""background-image: url("data:image/png;base64,{bin_str}");"""
except FileNotFoundError:
    bg_css = "background-color: #0E1117;"

st.markdown(f"""
    <style>
    /* Background Utama */
    .stApp {{
        {bg_css}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* --- KOTAK BARU UNTUK MEMBUNGKUS HASIL (Supaya Terbaca) --- */
    .result-container {{
        background-color: rgba(0, 0, 0, 0.8); /* Hitam pekat 80% transparan */
        padding: 30px;
        border-radius: 25px;
        border: 2px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        backdrop-filter: blur(10px); /* Efek blur di belakang kotak */
        box-shadow: 0 0 30px rgba(0,0,0,0.5); /* Bayangan luar kotak */
    }}

    /* Font Angka Raksasa */
    .big-font {{
        font-size: 180px !important;
        font-weight: bold;
        text-align: center;
        color: #FFFFFF;
        text-shadow: 0 0 20px #FF00FF; /* Neon Ungu */
        margin: 0;
        line-height: 1.2;
        font-family: 'Arial Black', sans-serif;
    }}
    
    /* Font Label */
    .medium-font {{
        font-size: 28px !important;
        text-align: center;
        color: #E0E0E0;
        margin-bottom: 10px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    
    /* Kotak Info Kecil (Atas) */
    .info-box {{
        background-color: rgba(0, 0, 0, 0.85);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #444;
        margin-bottom: 20px;
        color: white;
    }}
    
    .timestamp-text {{
        font-size: 16px;
        color: #FFD700;
        margin-top: 5px;
        font-family: monospace;
    }}

    /* Tombol */
    .stButton>button {{
        width: 100%;
        height: 70px;
        font-size: 22px;
        font-weight: bold;
        border-radius: 12px;
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
    }}
    .stButton>button:hover {{ transform: scale(1.02); filter: brightness(1.2); }}
    
    h1, h3 {{ color: white !important; text-shadow: 2px 2px 4px #000; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA UTAMA ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'is_revealed' not in st.session_state:
    st.session_state.is_revealed = False

def main():
    st.image("Voterastics.png")
    
    df = load_data('votes.json')
    if df is None:
        st.error("File 'votes (1).json' tidak ditemukan!")
        st.stop()

    total_votes = len(df)
    current_idx = st.session_state.current_index
    
    # Progress Bar
    progress = min(current_idx / total_votes, 1.0)
    st.progress(progress)

    # Selesai
    if current_idx >= total_votes:
        st.success("✅ SELESAI!")
        recap = df['candidate'].value_counts().reset_index()
        recap.columns = ['Kandidat', 'Jumlah Suara']
        st.table(recap)
        if st.button("Reset"):
            st.session_state.current_index = 0
            st.session_state.is_revealed = False
            st.rerun()
        st.stop()

    current_vote = df.iloc[current_idx]
    vote_timestamp = current_vote['timestamp'].strftime("%d %b %Y • %H:%M:%S WIB")

    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        # Info Box (Header)
        st.markdown(f"""
        <div class='info-box'>
            <div style='font-size: 24px; font-weight:bold;'>SUARA ONLINE #{current_idx + 1}</div>
            <div class='timestamp-text'>🕒 Diterima: {vote_timestamp}</div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.is_revealed:
            # --- TAMPILAN TERSEGEL (DIBUNGKUS KOTAK) ---
            st.markdown("""
            <div class='result-container'>
                <div style='text-align: center; font-size: 100px;'>🔒</div>
                <div class='medium-font'>SUARA TERSEGEL</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Spacer tombol
            st.write("")
            if st.button("🔓 BUKA SUARA"):
                with st.spinner('Membuka enkripsi...'):
                    time.sleep(0.0)
                st.session_state.is_revealed = True
                st.rerun()
        else:
            # --- TAMPILAN HASIL (DIBUNGKUS KOTAK) ---
            candidate_num = current_vote['candidate']
            st.markdown(f"""
            <div class='result-container'>
                <div class='medium-font'>Pilihan Pemilih:</div>
                <div class='big-font'>{candidate_num}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button("➡️ LANJUT KE SUARA BERIKUTNYA"):
                st.session_state.current_index += 1
                st.session_state.is_revealed = False
                st.rerun()

if __name__ == "__main__":
    main()
