import streamlit as st
import pandas as pd
import os

EXCEL_FILE = "transjakarta_updated.xlsx"

# ======================
# Load and Save Data
# ======================
@st.cache_data
def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=[
            "payUserID", "typeCard", "userName", "userSex", "userBirthYear",
            "transID", "routeID", "routeName", "corridorID", "corridorName",
            "transDate", "tapInHour", "tapOutHour", "duration", "payAmount", "direction"
        ])

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

df = load_data()

# ======================
# Streamlit App
# ======================
st.set_page_config("Aplikasi Transjakarta", layout="wide")
st.title("🚍 Aplikasi Transjakarta")

menu = st.sidebar.selectbox("Pilih Menu", ["Awal", "Cari Koridor"])

if menu == "Awal":
    pilihan = st.radio("Pilih:", ["Login", "Register"])

    if pilihan == "Login":
        pay_id = st.text_input("Masukkan Pay User ID")

        if st.button("Login"):
            if pay_id in df["payUserID"].astype(str).values:
                st.success("Login berhasil!")

                st.subheader("🔍 Cek Riwayat")
                if st.button("Lihat Profil"):
                    user = df[df["payUserID"] == pay_id].iloc[0]
                    st.write("**Nama**:", user["userName"])
                    st.write("**Jenis Kartu**:", user["typeCard"])
                    st.write("**Jenis Kelamin**:", user["userSex"])
                    st.write("**Tahun Lahir**:", user["userBirthYear"])

                if st.button("Lihat Riwayat"):
                    riwayat = df[df["payUserID"] == pay_id][[
                        "transID", "routeID", "transDate", "tapInHour",
                        "tapOutHour", "duration", "payAmount", "direction"
                    ]]
                    st.dataframe(riwayat)
            else:
                st.error("Pay User ID tidak ditemukan.")

    elif pilihan == "Register":
        st.subheader("📝 Form Registrasi")
        pay_id = st.text_input("Pay User ID")
        type_card = st.text_input("Jenis Kartu")
        user_name = st.text_input("Nama")
        user_sex = st.selectbox("Jenis Kelamin", ["Male", "Female"])
        birth_year = st.number_input("Tahun Lahir", min_value=1900, max_value=2025, step=1)

        if st.button("Simpan Registrasi"):
            if pay_id in df["payUserID"].astype(str).values:
                st.warning("User ID sudah terdaftar.")
            else:
                new_user = {
                    "payUserID": pay_id,
                    "typeCard": type_card,
                    "userName": user_name,
                    "userSex": user_sex,
                    "userBirthYear": birth_year
                }
                df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
                save_data(df)
                st.success("Registrasi berhasil!")

elif menu == "Cari Koridor":
    st.subheader("🔍 Cari Koridor")
    route_names = df["routeName"].dropna().unique().tolist()
    selected_route = st.selectbox("Pilih Nama Rute", sorted(route_names))

    if st.button("Cari"):
        result = df[df["routeName"] == selected_route][["corridorID", "corridorName"]].drop_duplicates()
        st.dataframe(result if not result.empty else pd.DataFrame([{"info": "Koridor tidak ditemukan"}]))
