import streamlit as st
import json
from collections import deque
from datetime import datetime, timedelta
from babel.dates import format_date
import os

# File untuk menyimpan riwayat rolling
HISTORY_FILE = "rolling_history.json"

# Fungsi untuk memuat riwayat rolling dari file
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = {}

# Fungsi untuk mendapatkan tanggal pengambilan usus kotor
# Jika hari ini Sabtu, maka tanggal yang ditampilkan adalah Senin
# Selain itu, tetap menampilkan besok
def get_tomorrow_date():
    today = datetime.today()  # Menggunakan today() agar sesuai zona waktu lokal
    if today.weekday() == 5:  # Jika hari ini Sabtu (5)
        target_date = today + timedelta(days=2)  # Lompat ke Senin
    else:
        target_date = today + timedelta(days=1)  # Besok untuk hari lainnya
    return target_date.strftime('%Y-%m-%d')  # Format YYYY-MM-DD untuk penyimpanan

# Fungsi untuk rolling data selain "WSF"
def roll_data(*datasets):
    queues = []
    
    for d in datasets:
        if not isinstance(d, dict):
            continue  # Skip jika data bukan dictionary

        filtered_values = []
        for v in d.values():
            if v != 'WSF':
                filtered_values.append(v)
        queues.append(deque(filtered_values))
    
    if queues and queues[0]:
        first_value = queues[0].popleft()
        
        for i in range(len(queues) - 1):
            if queues[i + 1]:
                queues[i].append(queues[i + 1].popleft())

        queues[-1].append(first_value)

    for i, d in enumerate(datasets):
        if not isinstance(d, dict):
            continue
        keys = list(d.keys())
        new_values = iter(queues[i])
        
        for k in keys:
            if d[k] != 'WSF':
                d[k] = next(new_values, d[k])

# Streamlit UI
st.title("Rolling Jadwal Pengambilan Usus Kotor")

# Daftar pilihan
perusahaan = ["--Pilih Perusahaan--", "Wahana Sejahtera Foods", "Phalosari Unggul Jaya"]
# Dropdown untuk pilih satu
selection = st.selectbox("Silakan pilih satu perusahaan:", perusahaan)

if selection == "Wahana Sejahtera Foods" and selection != "--Pilih Perusahaan--":
    # Atur dua kolom: kolom gambar dan kolom judul
    col1, col2 = st.columns([1, 4])  # rasio 1:4 agar gambar lebih kecil dari teks

    with col1:
        st.image("logo.png", width=130)  # ganti dengan path ke file gambar kamu

    with col2:
        st.markdown("<h1 style='margin-bottom: 0;'>Wahana Sejahtera Foods</h1>", unsafe_allow_html=True)
    
    # Membuat tab
    tabs = st.tabs(["Rolling", "Riwayat Rolling"])

    with tabs[0]:
        data_input = st.text_area("**Masukkan Data (format JSON):**")
        if st.button("Rolling", type="primary"):
            if data_input:
                try:
                    # Parse input menjadi dictionary
                    data = json.loads(data_input)

                    # Pastikan data memiliki key yang sesuai
                    required_keys = ["1", "2", "3", "5", "6"]
                    if not all(k in data for k in required_keys):
                        st.error("Data harus memiliki key: 1, 2, 3, 5, dan 6", icon="🚨")
                    else:
                        # Konversi key dari string ke integer
                        data = {int(k): v for k, v in data.items()}
                        
                        # Jalankan rolling
                        target_date = get_tomorrow_date()
                        st.write("\n**Bismillah...**\n")
                        st.write(f"**Jadwal pengambilan usus kotor {format_date(datetime.strptime(target_date, '%Y-%m-%d'), format='full', locale='id')}**")

                        roll_data(data[1], data[2], data[3], data[5], data[6])

                        # Menampilkan hasil rolling dalam format teks
                        for line, entries in data.items():
                            st.write(f'\nLine - {line}')
                            for key, value in entries.items():
                                st.write(f"{key}. {value}")

                        # Simpan hasil rolling berdasarkan tanggal
                        history[target_date] = data

                        # Simpan ke file JSON
                        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                            json.dump(history, f, indent=4, ensure_ascii=False)

                        # # Menampilkan hasil rolling dalam format JSON
                        # st.subheader("Hasil Rolling Untuk Rolling Selanjutnya")
                        # output_json = json.dumps({str(k): v for k, v in data.items()}, indent=4, ensure_ascii=False)
                        # st.text_area("Output JSON", output_json, height=300)

                except json.JSONDecodeError:
                    st.error("Format data tidak valid! Harap masukkan data dalam format JSON.", icon="⚠️")
            else:
                st.warning("Anda belum memasukkan data.", icon="⚠️")

    with tabs[1]:
        st.subheader("Riwayat Rolling")
        if history:
            selected_date = st.selectbox("Pilih Tanggal Rolling", list(history.keys()))
            if selected_date:
                # st.write(f"\n**Jadwal pengambilan usus kotor {format_date(datetime.strptime(selected_date, '%Y-%m-%d'), format='full', locale='id')}**")
                
                # Menampilkan hasil rolling dalam format JSON
                st.subheader("Hasil Rolling")
                history_json = json.dumps(history[selected_date], indent=4, ensure_ascii=False)
                st.text_area(" ", history_json, height=300)
                
                if st.button("Hapus Riwayat Tanggal Ini", type="secondary"):
                    del history[selected_date]
                    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                        json.dump(history, f, indent=4, ensure_ascii=False)
                    st.experimental_rerun()
        else:
            st.write("Belum ada data rolling yang tersimpan.")

if selection == "Phalosari Unggul Jaya" and selection != "--Pilih Perusahaan--":
    # Data lengkap
    data = {
        "1": "Pak Zainuri", "2": "Bu Nur", "3": "Bu Nur", "4": "Pak Lukman",
        "5": "Bu Yuni", "6": "Bu Sujadmi", "7": "Pak Zainuri", "8": "Pak Sudarsono",
        "9": "Pemuda 1", "10": "Pak Lukman", "11": "Pak Ferry", "12": "Pemuda 1",
        "13": "Pak Sudarsono", "14": "Pak Zainuri", "15": "Bu Nur", "16": "Bu Wulan",
        "17": "Bu Yuni", "18": "Pemuda 2", "19": "Pak Ferry", "20": "Pak Zainuri",
        "21": "Bu Nur", "22": "Pak Sudarsono", "23": "Pak Zainuri", "24": "Bu Yuni",
        "25": "Pak Ferry", "26": "Pemuda 1", "27": "Pak Zainuri", "28": "Pak Zainuri",
        "29": "Bu Nur", "30": "Paduka", "31": "Pak David", "32": "Pemuda 2",
        "33": "Pak Ferry", "34": "Pak Sudarsono", "35": "Paduka", "36": "Pak David",
        "37": "Bu Via", "38": "Bu Wulan", "39": "Pak Sudarsono", "40": "Pak Dicky",
        "41": "Bu Via", "42": "Bambang Haryanto", "43": "Bu Wulan", "44": "Pak Faizal",
        "45": "Moch. Slamet Febrianto", "46": "Bu Wulan", "47": "Pak Dicky", "48": "Bambang Haryanto",
        "49": "Pak Faizal", "50": "Moch. Slamet Febrianto", "51": "Formaju"
    }
    
    # Header dengan logo
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo puj.png", width=130)
    with col2:
        st.markdown("<h1 style='margin-bottom: 0;'>Phalosari Unggul Jaya</h1>", unsafe_allow_html=True)
    
    # Input tanggal dan rit libur
    awal = st.number_input("Rit Libur Awal:", min_value=0, max_value=51, value=0)
    akhir = st.number_input("Rit Libur Akhir:", min_value=0, max_value=51, value=0)
    pilih_potong_bebek = st.selectbox("Apakah Potong Bebek Libur?", ["--Pilih Satu--", "Libur", "Tidak Libur"])
    
    # Jumlah rit potong input jika Tidak Libur
    jumlah_potong = 0
    if pilih_potong_bebek == "Tidak Libur":
        jumlah_potong = st.number_input("Jumlah Rit Potong:", min_value=1, max_value=51, value=1)
    
    # Tanggal dan hari
    # tanggal = st.date_input("Pilih tanggal:", value=datetime.date.today())
    tanggal = st.date_input("Pilih tanggal:", value=datetime.today().date())
    hari_indo = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }
    hari = hari_indo[tanggal.strftime('%A')]
    st.markdown(f"<p style='margin-bottom:0'>*{hari}, {tanggal.strftime('%d / %m / %Y')}*</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-bottom:0'>Libur rit {awal} s/d {akhir}</p>", unsafe_allow_html=True)
    
    # Buat daftar libur
    if awal <= akhir:
        libur_keys = list(range(awal, akhir + 1))
    else:
        libur_keys = list(range(awal, 52)) + list(range(1, akhir + 1))
    
    # Ambil semua key (1–51), rotasi dari akhir + 1
    total_keys = list(range(1, 52))
    start = (akhir % 51) + 1
    rotated_keys = total_keys[start - 1:] + total_keys[:start - 1]
    
    # Rolling keys = yang tidak libur
    rolling_keys = [k for k in rotated_keys if k not in libur_keys]
    
    # Tentukan rolling result
    rolling_result = [(str(k), data[str(k)]) for k in rolling_keys]
    
    # Tentukan blok
    blok1, blok2, blok3 = [], [], []
    
    if pilih_potong_bebek == "Libur":
        # Semua rolling dibagi 2
        half = len(rolling_result) // 2
        blok1 = rolling_result[:half]
        blok2 = rolling_result[half:]
        blok3 = "Libur"
    elif pilih_potong_bebek == "Tidak Libur":
        # Cari key sebelum 'awal' yang tidak libur
        before_awal_keys = [k for k in rolling_keys if k < awal]
        if len(before_awal_keys) >= jumlah_potong:
            rpb_keys = before_awal_keys[-jumlah_potong:]
        else:
            sisa = jumlah_potong - len(before_awal_keys)
            rpb_keys = rolling_keys[-sisa:] + before_awal_keys
    
        # Hapus RPB keys dari rolling
        rolling_keys_final = [k for k in rolling_keys if k not in rpb_keys]
    
        rolling_result = [(str(k), data[str(k)]) for k in rolling_keys_final]
        blok3 = [(str(k), data[str(k)]) for k in rpb_keys]
    
        half = len(rolling_result) // 2
        blok1 = rolling_result[:half]
        blok2 = rolling_result[half:]
    
    # Fungsi untuk tampilkan blok
    def tampilkan_blok(judul, blok):
        hasil = f"<p style='margin-bottom:0'><b>*{judul}*</b></p>"
        if blok == "Libur":
            hasil += "Libur<br>"
        else:
            for i, (key, nama) in enumerate(blok, 1):
                hasil += f"{i}/{key}. {nama}<br>"
        return hasil
    
    # Tampilkan semua blok
    output = ""
    output += tampilkan_blok("RPA 1 PUJ - WSF (DO)", blok1)
    output += tampilkan_blok("RPA 2 PUJ - WSF (DO)", blok2)
    output += tampilkan_blok("RPB PUJ", blok3)
    st.markdown(output, unsafe_allow_html=True)











