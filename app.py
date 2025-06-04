import streamlit as st
import pandas as pd
import sqlite3
import os

# ==========================
# Inisialisasi database SQLite
# ==========================
DB_NAME = "transjakarta_users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            payUserID TEXT PRIMARY KEY,
            typeCard TEXT,
            userName TEXT,
            userSex TEXT,
            userBirthYear INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==========================
# Load data Excel
# ==========================
@st.cache_data
def load_data():
    df = pd.read_excel("TransJakarta_PIX.xlsx", sheet_name="FIX")
    df['payUserID'] = df['payUserID'].astype(str)
    return df

df = load_data()

# ==========================
# Helper DB
# ==========================
def get_user(payUserID):
    conn = sqlite3.connect(DB_NAME)
    user = pd.read_sql_query("SELECT * FROM users WHERE payUserID = ?", conn, params=(payUserID,))
    conn.close()
    return user

def insert_user(user_data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", user_data)
    conn.commit()
    conn.close()

# ==========================
# Session states
# ==========================
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def go_to(page):
    st.session_state.page = page

# ==========================
# Halaman Login
# ==========================
def login_page():
    st.title("🙌🏻 Selamat Datang Pengguna TransJakarta!")

    pay_id = st.text_input("Masukkan PayUserID:")
    login = st.button("Login")
    register = st.button("Register")

    if login:
        user = get_user(pay_id)
        if not user.empty:
            st.session_state.user_id = pay_id
            go_to('main_menu')
        else:
            st.error("PayUserID tidak ditemukan. Silakan registrasi.")

    if register:
        go_to('register')

# ==========================
# Halaman Registrasi
# ==========================
def register_page():
    st.title("📝 Register Pengguna Baru")

    payUserID = st.text_input("PayUserID")
    typeCard = st.selectbox("Jenis Kartu", ["BRIZZI", "E-Money", "Flazz", "JakCard", "MegaCash", "TapCash"])
    userName = st.text_input("Nama")
    userSex = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    userBirthYear = st.number_input("Tahun Lahir", min_value=1900, max_value=2025, value=2000)

    if st.button("Daftar"):
        if not payUserID.strip() or not userName.strip():
            st.error("Semua kolom harus diisi!")
        elif not payUserID.isdigit() or len(payUserID) != 12:
            st.error("PayUserID harus terdiri dari 12 digit angka.")
        elif not get_user(payUserID).empty:
            st.error("PayUserID sudah terdaftar.")
        else:
            insert_user((payUserID, typeCard, userName, userSex, userBirthYear))
            st.success("Registrasi berhasil!")
            go_to('login')

    if st.button("Kembali"):
        go_to('login')

# ==========================
# Halaman Menu Utama
# ==========================
def main_menu():
    user = get_user(st.session_state.user_id).iloc[0]
    st.title(f"👋 Selamat datang, {user['userName']}!")

    if st.button("Cari Kode Koridor"):
        go_to('corridor')
    if st.button("Cek Riwayat"):
        go_to('history')
    if st.button("Logout"):
        st.session_state.user_id = None
        go_to('login')

# ==========================
# Cari Koridor
# ==========================
def corridor_page():
    st.title("🛣️ Cari Kode Koridor")

    route_list = df['routeName'].dropna().unique().tolist()
    selected_route = st.selectbox("Pilih atau ketik nama rute:", sorted(route_list), placeholder="Contoh: Rute 1")

    if selected_route and st.button("Cari"):
        matched = df[df['routeName'] == selected_route]
        if not matched.empty:
            st.success(f"✅ Kode Koridor: {matched.iloc[0]['corridorID']}")
        else:
            st.error("❌ Kode koridor tidak ditemukan.")

    if st.button("Kembali"):
        go_to('main_menu')

# ==========================
# Riwayat Perjalanan
# ==========================
def history_page():
    st.title("📜 Riwayat Perjalanan")

    user = get_user(st.session_state.user_id).iloc[0]
    st.write(f"**Nama**: {user['userName']}")
    st.write(f"**Tipe Kartu**: {user['typeCard']}")
    st.write(f"**Jenis Kelamin**: {user['userSex']}")
    st.write(f"**Tahun Lahir**: {user['userBirthYear']}")

    history = df[df['payUserID'] == st.session_state.user_id][[
        'transID', 'routeID', 'transDate', 'tapInTime', 'tapOutTime', 'duration', 'direction'
    ]]

    if history.empty:
        st.warning("⚠️ Tidak ada riwayat perjalanan.")
    else:
        st.dataframe(history.reset_index(drop=True))

    if st.button("Kembali"):
        go_to('main_menu')

# ==========================
# Routing Halaman
# ==========================
if st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'register':
    register_page()
elif st.session_state.page == 'main_menu':
    main_menu()
elif st.session_state.page == 'corridor':
    corridor_page()
elif st.session_state.page == 'history':
    history_page()
