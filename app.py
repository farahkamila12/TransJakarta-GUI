import streamlit as st
import pandas as pd
import os

EXCEL_FILE = "transjakarta pixxx.xlsx"

# ==========================
# Load & Save Data
# ==========================
@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE, sheet_name="transjakarta")

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False, sheet_name="transjakarta")

df = load_data()

# ==========================
# Fungsi
# ==========================
def get_user_profile(pay_id):
    data = df[df['payUserID'] == pay_id]
    if data.empty:
        return None
    user = data.iloc[0]
    return {
        "Nama": user["userName"],
        "Jenis Kartu": user["typeCard"],
        "Jenis Kelamin": user["userSex"],
        "Tahun Lahir": user["userBirthYear"]
    }

def get_user_history(pay_id):
    return df[df["payUserID"] == pay_id][[
        'transID', 'routeID', 'transDate', 'tapInHour', 'tapOutHour',
        'duration', 'payAmount', 'direction'
    ]]

def search_corridor(route_name):
    return df[df['routeName'] == route_name][['corridorID', 'corridorName']].drop_duplicates()

# ==========================
# Aplikasi Streamlit
# ==========================
st.set_page_config(page_title="Aplikasi Transjakarta", layout="wide")
st.title("🚍 Aplikasi Transjakarta")

menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Cari Koridor"])

if menu == "Login":
    pay_id = st.text_input("Masukkan Pay User ID")

    if st.button("Login"):
        if pay_id in df['payUserID'].astype(str).values:
            st.success("Login berhasil!")
            profile = get_user_profile(pay_id)
            if profile:
                st.subheader("👤 Profil Pengguna")
                for k, v in profile.items():
                    st.write(f"**{k}**: {v}")

            if st.button("Tampilkan Riwayat"):
                st.subheader("📈 Riwayat Perjalanan")
                history = get_user_history(pay_id)
                st.dataframe(history)
        else:
            st.error("Pay User ID tidak ditemukan.")

elif menu == "Register":
    st.subheader("📝 Registrasi Pengguna Baru")
    new_id = st.text_input("Pay User ID")
    name = st.text_input("Nama")
    card = st.text_input("Jenis Kartu")
    sex = st.selectbox("Jenis Kelamin", ["Male", "Female"])
    birth = st.number_input("Tahun Lahir", min_value=1900, max_value=2025, step=1)

    if st.button("Daftar"):
        if new_id in df["payUserID"].astype(str).values:
            st.warning("User ID sudah ada.")
        else:
            new_user = {
                "payUserID": new_id,
                "userName": name,
                "typeCard": card,
                "userSex": sex,
                "userBirthYear": birth
            }
            df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
            save_data(df)
            st.success("Registrasi berhasil!")

elif menu == "Cari Koridor":
    st.subheader("🔍 Cari Koridor Berdasarkan Rute")
    route_list = df['routeName'].dropna().unique().tolist()
    selected_route = st.selectbox("Pilih Rute", sorted(route_list))

    if st.button("Cari Koridor"):
        result = search_corridor(selected_route)
        if not result.empty:
            st.dataframe(result)
        else:
            st.info("Koridor tidak ditemukan.")
