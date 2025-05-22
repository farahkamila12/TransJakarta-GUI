import streamlit as st
import pandas as pd

# ==========================
# Load Data
# ==========================
@st.cache_data
def load_data():
    return pd.read_excel("transjakarta pixxx.xlsx", sheet_name="transjakarta")

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

menu = st.sidebar.radio("Menu", ["Login", "Cari Koridor"])

if menu == "Login":
    pay_id = st.text_input("Masukkan PayCard ID")

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
                st.dataframe(get_user_history(pay_id))
        else:
            st.error("PayCard ID tidak ditemukan.")

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
