import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Data untuk username dan password
users = {
    "Basket": "123",
    "Badminton": "123", 
    "Nando": "123",
    "Ara": "123",
    "Adhit": "123", 
    "Nafi": "123",
    "Viewer": "123"
}

# Fungsi untuk menyimpan data ke file
def save_data():
    if "user_data" in st.session_state:
        with open('user_data.json', 'w') as f:
            json.dump(st.session_state["user_data"], f)

# Fungsi untuk memuat data dari file
def load_data():
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            st.session_state["user_data"] = json.load(f)
    else:
        st.session_state["user_data"] = {}

# Fungsi untuk format rupiah tanpa locale
def format_rupiah(amount):
    return f"Rp {amount:,.0f}"

# Fungsi untuk halaman Sign In
def sign_in():
    # Load data saat aplikasi dimulai
    if "user_data" not in st.session_state:
        load_data()
        
    st.title("Sign In")
    st.info("Jika anda bukan seorang admin, silahkan ketik viewer di username dan pilih user yang ingin anda lihat")
    
    # Input untuk username dan password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Konversi username ke format yang benar
    corrected_username = None
    for valid_user in users.keys():
        if username.lower() == valid_user.lower():
            corrected_username = valid_user
            break
    
    # Jika username adalah viewer, tampilkan select box untuk memilih user yang akan dilihat
    if corrected_username == "Viewer" or username.lower() == "viewer":
        available_users = ["Basket", "Badminton", "Nando", "Ara", "Adhit", "Nafi"]
        selected_user = st.selectbox("Pilih user yang akan dilihat:", available_users)
        if "selected_user" not in st.session_state:
            st.session_state["selected_user"] = selected_user
    
    # Cek jika login button ditekan
    if st.button("Login"):
        if corrected_username and users[corrected_username] == password:
            # Menyimpan status login di session state
            st.session_state["logged_in"] = True
            st.session_state["username"] = corrected_username
            if corrected_username == "Viewer":
                st.session_state["selected_user"] = selected_user
            st.session_state["page"] = "second_page"
            
            # Inisialisasi data untuk user jika belum ada
            if corrected_username not in st.session_state["user_data"] and corrected_username != "Viewer":
                st.session_state["user_data"][corrected_username] = []
                save_data()  # Simpan perubahan
                
            st.rerun()
        else:
            st.error("Username atau password salah! Silakan coba lagi.")

# Fungsi untuk halaman kedua
def second_page():
    st.title("Selamat Datang!")
    st.write(f"Halo, {st.session_state['username']}! Anda berhasil login.")
    
    username = st.session_state["username"]
    
    if username == "Viewer":
        # Tampilan khusus untuk viewer
        st.header("Data Pembayaran")
        target_user = st.session_state["selected_user"]
        
        if "user_data" in st.session_state and st.session_state["user_data"]:
            # Gabungkan semua data user
            all_data = []
            
            # Hanya ambil data dari user yang sesuai
            if target_user in st.session_state["user_data"]:
                for item in st.session_state["user_data"][target_user]:
                    item_with_user = item.copy()
                    item_with_user["username"] = target_user
                    all_data.append(item_with_user)
            
            if all_data:
                df = pd.DataFrame(all_data)
                
                # Filter status, jenis, dan nama
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_filter = st.selectbox("Filter Status", ["Semua", "Sudah Bayar", "Belum Bayar"])
                with col2:
                    jenis_list = ["Semua"] + list(df["jenis"].unique())
                    jenis_filter = st.selectbox("Filter Jenis", jenis_list)
                with col3:
                    nama_list = ["Semua"] + list(df["nama"].unique())
                    nama_filter = st.selectbox("Filter Nama", nama_list)
                
                # Terapkan filter
                if status_filter != "Semua":
                    df = df[df["status"] == status_filter]
                if jenis_filter != "Semua":
                    df = df[df["jenis"] == jenis_filter]
                if nama_filter != "Semua":
                    df = df[df["nama"] == nama_filter]
                
                if not df.empty:
                    # Format harga ke Rupiah
                    df["harga"] = df["harga"].apply(format_rupiah)
                    
                    # Deteksi device
                    is_mobile = st.session_state.get('is_mobile', len(st.session_state) < 4)
                    
                    if is_mobile:
                        # Tampilan mobile - card style
                        for idx, row in df.iterrows():
                            with st.container():
                                st.markdown("---")
                                st.write(f"**Username:** {row['username']}")
                                st.write(f"**Jenis:** {row['jenis']}")
                                st.write(f"**Nama:** {row['nama']}")
                                st.write(f"**Tanggal:** {row['tanggal']}")
                                st.write(f"**Harga:** {row['harga']}")
                                
                                user = row["username"]
                                data_idx = st.session_state["user_data"][user].index(next(item for item in st.session_state["user_data"][user] if item["nama"] == row["nama"] and item["tanggal"] == row["tanggal"]))
                                old_status = st.session_state["user_data"][user][data_idx]["status"]
                                
                                col1, col2 = st.columns([2,2])
                                with col1:
                                    st.write("**Status:**")
                                with col2:
                                    status = st.selectbox("Status Pembayaran", ["Belum Bayar", "Sudah Bayar"], 
                                                        index=0 if old_status == "Belum Bayar" else 1, 
                                                        key=f"status_{user}_{idx}",
                                                        label_visibility="collapsed")
                                
                                if old_status != status:
                                    if status == "Sudah Bayar":
                                        st.session_state["user_data"][user][data_idx]["tanggal_bayar"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    else:
                                        st.session_state["user_data"][user][data_idx]["tanggal_bayar"] = None
                                    st.session_state["user_data"][user][data_idx]["status"] = status
                                    save_data()
                                    st.rerun()
                                
                                st.write(f"**Tanggal Bayar:** {row['tanggal_bayar'] if 'tanggal_bayar' in row and row['tanggal_bayar'] else '-'}")
                    else:
                        # Tampilan desktop - table style
                        col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,2,2,2,2,2])
                        with col1:
                            st.write("**Username**")
                        with col2:
                            st.write("**Jenis**")
                        with col3:
                            st.write("**Nama**")
                        with col4:
                            st.write("**Tanggal**")
                        with col5:
                            st.write("**Harga**")
                        with col6:
                            st.write("**Status**")
                        with col7:
                            st.write("**Tanggal Bayar**")
                        
                        for idx, row in df.iterrows():
                            col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,2,2,2,2,2])
                            with col1:
                                st.write(row["username"])
                            with col2:
                                st.write(row["jenis"])
                            with col3:
                                st.write(row["nama"])
                            with col4:
                                st.write(row["tanggal"])
                            with col5:
                                st.write(row["harga"])
                            with col6:
                                user = row["username"]
                                data_idx = st.session_state["user_data"][user].index(next(item for item in st.session_state["user_data"][user] if item["nama"] == row["nama"] and item["tanggal"] == row["tanggal"]))
                                old_status = st.session_state["user_data"][user][data_idx]["status"]
                                status = st.selectbox("Status Pembayaran", ["Belum Bayar", "Sudah Bayar"], 
                                                    index=0 if old_status == "Belum Bayar" else 1, 
                                                    key=f"status_{user}_{idx}",
                                                    label_visibility="collapsed")
                                
                                if old_status != status:
                                    if status == "Sudah Bayar":
                                        st.session_state["user_data"][user][data_idx]["tanggal_bayar"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    else:
                                        st.session_state["user_data"][user][data_idx]["tanggal_bayar"] = None
                                    st.session_state["user_data"][user][data_idx]["status"] = status
                                    save_data()
                                    st.rerun()
                            with col7:
                                st.write(row["tanggal_bayar"] if "tanggal_bayar" in row and row["tanggal_bayar"] else "-")
                else:
                    st.info("Tidak ada data yang sesuai dengan filter yang dipilih")
            else:
                st.info("Belum ada data pembayaran")
    else:
        # Tampilan untuk user biasa
        tab1, tab2, tab3 = st.tabs(["Input Data", "Data Pembayaran", "Histori Pembayaran"])
        
        with tab1:
            st.header("Input Data Baru")
            
            # Inisialisasi session state untuk form fields jika belum ada
            if "form_jenis" not in st.session_state:
                st.session_state["form_jenis"] = ""
            if "form_nama" not in st.session_state:
                st.session_state["form_nama"] = ""
            if "form_harga" not in st.session_state:
                st.session_state["form_harga"] = 0
                
            # Form input
            with st.form("input_form"):
                jenis = st.text_input("Jenis", value=st.session_state["form_jenis"], key="jenis_input")
                nama = st.text_input("Nama", value=st.session_state["form_nama"], key="nama_input")
                tanggal = st.date_input("Tanggal")
                harga = st.number_input("Harga (Rp)", value=st.session_state["form_harga"], min_value=0, step=1000, key="harga_input")
                
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    if nama and harga > 0 and jenis:
                        # Tambah data baru
                        new_data = {
                            "jenis": jenis,
                            "nama": nama,
                            "tanggal": tanggal.strftime("%Y-%m-%d"),
                            "harga": harga,
                            "status": "Belum Bayar",
                            "tanggal_bayar": None
                        }
                        
                        if username not in st.session_state["user_data"]:
                            st.session_state["user_data"][username] = []
                        
                        st.session_state["user_data"][username].append(new_data)
                        save_data()  # Simpan perubahan
                        st.success("Data berhasil ditambahkan!")
                        
                        # Reset form fields setelah submit
                        st.session_state["form_jenis"] = ""
                        st.session_state["form_nama"] = ""
                        st.session_state["form_harga"] = 0
                    else:
                        st.error("Mohon isi semua field dengan benar")
        
        with tab2:
            st.header("Data Pembayaran")
            
            if username in st.session_state["user_data"] and st.session_state["user_data"][username]:
                # Filter status
                status_filter = st.selectbox("Filter Status", ["Semua", "Sudah Bayar", "Belum Bayar"])
                
                # Buat DataFrame dari data user
                df = pd.DataFrame(st.session_state["user_data"][username])
                
                # Terapkan filter
                if status_filter != "Semua":
                    df = df[df["status"] == status_filter]
                
                if not df.empty:
                    # Format harga ke Rupiah
                    df["harga"] = df["harga"].apply(format_rupiah)
                    
                    # Tampilkan header
                    col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,2,2])
                    with col1:
                        st.write("**Jenis**")
                    with col2:
                        st.write("**Nama**") 
                    with col3:
                        st.write("**Tanggal**")
                    with col4:
                        st.write("**Harga**")
                    with col5:
                        st.write("**Status**")
                    with col6:
                        st.write("**Action**")
                    
                    # Tampilkan setiap baris dengan dropdown status dan tombol hapus
                    for idx, row in df.iterrows():
                        col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,2,2])
                        
                        with col1:
                            st.write(row["jenis"])
                        with col2:
                            st.write(row["nama"])
                        with col3:
                            st.write(row["tanggal"])
                        with col4:
                            st.write(row["harga"])
                        with col5:
                            old_status = st.session_state["user_data"][username][idx]["status"]
                            status = st.selectbox("Status Pembayaran", ["Belum Bayar", "Sudah Bayar"], index=0 if old_status == "Belum Bayar" else 1, key=f"status_{idx}", label_visibility="collapsed")
                            # Update status dan tanggal bayar di session state
                            if old_status != status and status == "Sudah Bayar":
                                st.session_state["user_data"][username][idx]["tanggal_bayar"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state["user_data"][username][idx]["status"] = status
                            save_data()  # Simpan perubahan
                        with col6:
                            if st.button("Hapus", key=f"delete_{idx}"):
                                st.session_state["user_data"][username].pop(idx)
                                save_data()  # Simpan perubahan
                                st.rerun()
                else:
                    st.info(f"Tidak ada data dengan status {status_filter}")
            else:
                st.info("Belum ada data pembayaran")
        
        with tab3:
            st.header("Histori Pembayaran")
            
            if username in st.session_state["user_data"] and st.session_state["user_data"][username]:
                # Filter data yang sudah bayar
                paid_data = [data for data in st.session_state["user_data"][username] 
                            if data["status"] == "Sudah Bayar"]
                
                if paid_data:
                    # Buat DataFrame dari data yang sudah bayar
                    df_paid = pd.DataFrame(paid_data)
                    
                    # Format harga ke Rupiah
                    df_paid["harga"] = df_paid["harga"].apply(format_rupiah)
                    
                    # Tampilkan header
                    col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,2,2])
                    with col1:
                        st.write("**Jenis**")
                    with col2:
                        st.write("**Nama**") 
                    with col3:
                        st.write("**Tanggal**")
                    with col4:
                        st.write("**Harga**")
                    with col5:
                        st.write("**Status**")
                    with col6:
                        st.write("**Tanggal Bayar**")
                    
                    # Tampilkan setiap baris
                    for idx, row in df_paid.iterrows():
                        col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,2,2])
                        
                        with col1:
                            st.write(row["jenis"])
                        with col2:
                            st.write(row["nama"])
                        with col3:
                            st.write(row["tanggal"])
                        with col4:
                            st.write(row["harga"])
                        with col5:
                            st.write(row["status"])
                        with col6:
                            st.write(row["tanggal_bayar"] if row["tanggal_bayar"] else "-")
                else:
                    st.info("Belum ada histori pembayaran")
            else:
                st.info("Belum ada data pembayaran")
    
    if st.button("Logout"):
        logout()
        st.rerun()

# Fungsi Logout
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["page"] = "sign_in"
    # Data tetap tersimpan di user_data sehingga tersedia saat login kembali

# Logika utama aplikasi
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["page"] = "sign_in"

# Load data saat aplikasi dimulai
if "user_data" not in st.session_state:
    load_data()

# Navigasi berdasarkan session_state["page"]
if st.session_state["page"] == "sign_in" and not st.session_state["logged_in"]:
    sign_in()  # Tampilkan halaman login jika belum login
elif st.session_state["page"] == "second_page" and st.session_state["logged_in"]:
    second_page()  # Tampilkan halaman kedua jika sudah login
