import streamlit as st
import pandas as pd
from datetime import datetime
import locale

# Set locale untuk format Rupiah
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

# Data untuk username dan password
users = {
    "Admin Basket": "123",
    "Admin Badminton": "123", 
    "Nando": "123",
    "Ara": "123",
    "Adhit": "123", 
    "Nafi": "123",
    "Viewer Badminton": "123",
    "Viewer Basket": "123",
}

# Fungsi untuk halaman Sign In
def sign_in():
    st.title("Sign In")
    
    # Input untuk username dan password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Cek jika login button ditekan
    if st.button("Login"):
        if username in users and users[username] == password:
            # Menyimpan status login di session state
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["page"] = "second_page"
            
            # Inisialisasi data untuk user jika belum ada
            if "user_data" not in st.session_state:
                st.session_state["user_data"] = {}
            if username not in st.session_state["user_data"] and username != "viewer":
                st.session_state["user_data"][username] = []
                
            st.rerun()
        else:
            st.error("Username atau password salah! Silakan coba lagi.")

# Fungsi untuk halaman kedua
def second_page():
    st.title("Selamat Datang!")
    st.write(f"Halo, {st.session_state['username']}! Anda berhasil login.")
    
    username = st.session_state["username"]
    
    if username in ["Viewer Badminton", "Viewer Basket"]:
        # Tampilan khusus untuk viewer
        st.header("Data Semua Users")
        
        if "user_data" in st.session_state and st.session_state["user_data"]:
            # Gabungkan semua data user
            all_data = []
            admin_type = "Admin Badminton" if username == "Viewer Badminton" else "Admin Basket"
            
            # Hanya ambil data dari admin yang sesuai
            if admin_type in st.session_state["user_data"]:
                for item in st.session_state["user_data"][admin_type]:
                    item_with_user = item.copy()
                    item_with_user["username"] = admin_type
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
                    df["harga"] = df["harga"].apply(lambda x: locale.currency(x, grouping=True))
                    
                    # Tampilkan header
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
                    
                    # Tampilkan setiap baris
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
                            status = st.selectbox("Status Pembayaran", ["Belum Bayar", "Sudah Bayar"], index=0 if old_status == "Belum Bayar" else 1, key=f"status_{user}_{idx}", label_visibility="collapsed")
                            if old_status != status:
                                if status == "Sudah Bayar":
                                    st.session_state["user_data"][user][data_idx]["tanggal_bayar"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    st.session_state["user_data"][user][data_idx]["tanggal_bayar"] = None
                                st.session_state["user_data"][user][data_idx]["status"] = status
                                st.rerun()
                        with col7:
                            st.write(row["tanggal_bayar"] if "tanggal_bayar" in row and row["tanggal_bayar"] else "-")
                else:
                    st.info("Tidak ada data yang sesuai dengan filter yang dipilih")
            else:
                st.info("Belum ada data pembayaran dari admin")
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
                    df["harga"] = df["harga"].apply(lambda x: locale.currency(x, grouping=True))
                    
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
                        with col6:
                            if st.button("Hapus", key=f"delete_{idx}"):
                                st.session_state["user_data"][username].pop(idx)
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
                    df_paid["harga"] = df_paid["harga"].apply(lambda x: locale.currency(x, grouping=True))
                    
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

# Navigasi berdasarkan session_state["page"]
if st.session_state["page"] == "sign_in" and not st.session_state["logged_in"]:
    sign_in()  # Tampilkan halaman login jika belum login
elif st.session_state["page"] == "second_page" and st.session_state["logged_in"]:
    second_page()  # Tampilkan halaman kedua jika sudah login
