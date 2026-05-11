import streamlit as st
import json
from collections import deque
from datetime import datetime, timedelta
from babel.dates import format_date
import os

# File untuk menyimpan riwayat rolling
HISTORY_FILE = "rolling_history.json"

# Load history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = {}

# =========================
# LIST NAMA UNTUK MULTISELECT
# =========================
nama_list = [
    "Abdul Minin",
    "Anang Zamzami",
    "Bambang Harianto",
    "Desta",
    "Eko Budi",
    "FORMAJU",
    "FORMAJU I",
    "Hermanto",
    "Heru Susanto",
    "Ismail",
    "Karang Taruna Bulak",
    "Karang Taruna Doyong",
    "Karang Taruna Garas",
    "Karang Taruna Gilang",
    "Karang Taruna Gondang II",
    "Karang Taruna Jabon",
    "Karang Taruna PBPB",
    "Karang Taruna Paras",
    "Karang Taruna PG",
    "Karang Taruna Singorejo",
    "Karang Taruna Singorejo I",
    "Karang Taruna Tamtama I",
    "Karang Taruna Tamtama II",
    "Karang Taruna Tawang",
    "Karang Taruna Turi Pinggir",
    "Kartar BS 1",
    "Kartar BS 2",
    "Linda Wulan Prihantini",
    "Nur Laili",
    "PBGR Bejo",
    "Rudiyanto",
    "Siti Mu'awanah",
    "Siti Rodhiyah",
    "Sugeng",
    "Sukamto",
    "wsf",
    "Zainuddin"
]

# =========================
# FUNCTION
# =========================
def get_tomorrow_date():
    today = datetime.today()
    if today.weekday() == 5:  # Sabtu
        target_date = today + timedelta(days=2)
    else:
        target_date = today + timedelta(days=1)
    return target_date.strftime('%Y-%m-%d')

def roll_data(*datasets):
    queues = []
    valid_indices = []

    # Ambil queue + tandai yang valid
    for idx, d in enumerate(datasets):
        if not isinstance(d, dict):
            queues.append(deque())
            continue

        filtered = [
            v for v in d.values()
            if str(v).strip().lower() != 'wsf'
        ]

        if filtered:
            queues.append(deque(filtered))
            valid_indices.append(idx)
        else:
            queues.append(deque())

    # 🔥 rolling hanya antar group yang ada isinya
    if len(valid_indices) > 1:
        first_idx = valid_indices[0]
        first_value = queues[first_idx].popleft()

        for i in range(len(valid_indices) - 1):
            curr = valid_indices[i]
            nxt = valid_indices[i + 1]

            if queues[nxt]:
                queues[curr].append(queues[nxt].popleft())

        queues[valid_indices[-1]].append(first_value)

    # assign balik
    for idx, d in enumerate(datasets):
        if not isinstance(d, dict):
            continue

        new_values = iter(queues[idx])

        for k in d.keys():
            if str(d[k]).strip().lower() != 'wsf':
                d[k] = next(new_values, d[k])

# =========================
# UI
# =========================
st.title("Rolling Jadwal Pengambilan Usus Kotor")

perusahaan = ["--Pilih Perusahaan--", "Wahana Sejahtera Foods", "Phalosari Unggul Jaya"]
selection = st.selectbox("Silakan pilih satu perusahaan:", perusahaan)

# =========================
# WSF
# =========================
if selection == "Wahana Sejahtera Foods" and selection != "--Pilih Perusahaan--":

    col1, col2 = st.columns([1, 4])

    with col1:
        st.image("logo.png", width=130)

    with col2:
        st.markdown("<h1 style='margin-bottom: 0;'>Wahana Sejahtera Foods</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Rolling", "Riwayat Rolling"])

    # =========================
    # TAB ROLLING
    # =========================
    with tabs[0]:

        data_input = st.text_area("**Masukkan Data (format JSON):**")

        # 🔥 MULTISELECT TAMBAHAN
        selected_nama = st.multiselect(
            "Pilih nama yang *Tunggu Pembayaran*:",
            nama_list
        )

        if st.button("Rolling", type="primary"):
            if data_input:
                try:
                    data = json.loads(data_input)

                    required_keys = ["1", "2", "3", "5", "6"]
                    if not all(k in data for k in required_keys):
                        st.error("Data harus memiliki key: 1, 2, 3, 5, dan 6", icon="🚨")
                    else:
                        data = {int(k): v for k, v in data.items()}
                        
                        target_date = get_tomorrow_date()

                        # st.write("\n**Bismillah...**\n")
                        # st.write(f"**Jadwal pengambilan usus kotor {format_date(datetime.strptime(target_date, '%Y-%m-%d'), format='full', locale='id')}**")

                        roll_data(data[1], data[2], data[3], data[5], data[6])

                        # =========================
                        # 🔥 FORMAT OUTPUT WA
                        # =========================
                        selected_nama_lower = {n.lower() for n in selected_nama}
                        
                        output_text = ""
                        
                        output_text += "Bismillah...\n\n"
                        output_text += f"Jadwal pengambilan usus kotor {format_date(datetime.strptime(target_date, '%Y-%m-%d'), format='full', locale='id')}\n\n"
                        
                        history_data = {}
                        
                        for line, entries in data.items():
                            output_text += f"Line - {line}\n"
                        
                            history_data[line] = {}
                        
                            for key, value in entries.items():
                        
                                clean_value = value.replace(" *(Tunggu Pembayaran)*", "")
                        
                                # tampilkan label jika dipilih
                                display_value = clean_value
                                if clean_value.lower() in selected_nama_lower:
                                    display_value = f"{clean_value} *(Tunggu Pembayaran)*"
                        
                                output_text += f"{key}. {display_value}\n"
                        
                                # simpan tanpa label
                                history_data[line][key] = clean_value
                        
                            output_text += "\n"
                        
                        # 🔥 tampilkan ke text area (biar bisa dicopy)
                        st.text_area("", output_text, height=400)
                        
                        # simpan history
                        history[target_date] = history_data
                        
                        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                            json.dump(history, f, indent=4, ensure_ascii=False)

                        # roll_data(data[1], data[2], data[3], data[5], data[6])

                        # # =========================
                        # # 🔥 TAMBAHAN LOGIC LABEL
                        # # =========================
                        # # 🔥 copy data khusus untuk history (bersih)
                        # history_data = {}
                        
                        # for line, entries in data.items():
                        #     st.markdown(f"**Line - {line}**")
                        
                        #     history_data[line] = {}
                        
                        #     for key, value in entries.items():
                        
                        #         # 🔥 pastikan bersih dulu
                        #         clean_value = value.replace(" *(Tunggu Pembayaran)*", "")
                        
                        #         # =========================
                        #         # TAMPILAN (ADA LABEL)
                        #         # =========================
                        #         selected_nama_lower = {n.lower() for n in selected_nama}
                                
                        #         display_value = clean_value
                        #         if clean_value.lower() in selected_nama_lower:
                        #             display_value = f"{clean_value} \\*(Tunggu Pembayaran)\\*"
                        
                        #         st.markdown(f"{key}. {display_value}")
                        
                        #         # =========================
                        #         # SIMPAN (TANPA LABEL)
                        #         # =========================
                        #         history_data[line][key] = clean_value

                        # history[target_date] = history_data

                        # with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                        #     json.dump(history, f, indent=4, ensure_ascii=False)

                except json.JSONDecodeError:
                    st.error("Format data tidak valid!", icon="⚠️")
            else:
                st.warning("Anda belum memasukkan data.", icon="⚠️")

    # =========================
    # TAB HISTORY
    # =========================
    with tabs[1]:
        st.subheader("Riwayat Rolling")
        if history:
            selected_date = st.selectbox("Pilih Tanggal Rolling", list(history.keys()))
            if selected_date:
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

# =========================
# PUJ (TIDAK DIUBAH)
# =========================
if selection == "Phalosari Unggul Jaya" and selection != "--Pilih Perusahaan--":

    data = {
        "1": "Pak Zainuri", "2": "Bu Nur", "3": "Bu Nur", "4": "Pak Lukman",
        "5": "Arifin", "6": "Zainuddin", "7": "Pak Zainuri", "8": "Pak Sudarsono",
        "9": "Pemuda 1", "10": "Pak Lukman", "11": "Pak Ferry", "12": "Pemuda 1",
        "13": "Pak Sudarsono", "14": "Pak Zainuri", "15": "Bu Nur", "16": "Bu Wulan",
        "17": "Arifin", "18": "Pemuda 2", "19": "Pak Ferry", "20": "Pak Zainuri",
        "21": "Bu Nur", "22": "Pak Sudarsono", "23": "Pak Zainuri", "24": "Arifin",
        "25": "Pak Ferry", "26": "Pemuda 1", "27": "Pak Zainuri", "28": "Pak Zainuri",
        "29": "Bu Nur", "30": "Paduka", "31": "Pak David", "32": "Pemuda 2",
        "33": "Pak Ferry", "34": "Pak Sudarsono", "35": "Paduka", "36": "Pak David",
        "37": "Bu Via", "38": "Bu Wulan", "39": "Pak Sudarsono", "40": "Pak Dicky",
        "41": "Bu Via", "42": "Bambang Haryanto", "43": "Bu Wulan", "44": "Arifin",
        "45": "Moch. Slamet Febrianto", "46": "Bu Wulan", "47": "Pak Dicky", "48": "Bambang Haryanto",
        "49": "Arifin", "50": "Moch. Slamet Febrianto", "51": "Formaju"
    }

    nama_list_puj = [
        "Pak Zainuri",
        "Bu Nur",
        "Pak Lukman",
        "Arifin",
        "Zainuddin",
        "Pak Sudarsono",
        "Pemuda 1",
        "Pak Ferry",
        "Bu Wulan",
        "Pemuda 2",
        "Paduka",
        "Pak David",
        "Bu Via",
        "Pak Dicky",
        "Bambang Haryanto",
        "Moch. Slamet Febrianto",
        "Formaju"
    ]

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

    nama_list_puj = sorted(nama_list_puj, key=lambda x: x.lower())
    
    selected_nama_puj = st.multiselect(
        "Pilih nama yang *Tunggu Pembayaran* (PUJ):",
        nama_list_puj
    )

    # nama_list_puj = sorted(nama_list_puj)
    
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
    
                # 🔥 bersihkan label lama
                clean_nama = nama.replace(" *(Tunggu Pembayaran)*", "")
    
                # 🔥 kasih label jika dipilih
                selected_nama_puj_lower = {n.lower() for n in selected_nama_puj}

                if clean_nama.lower() in selected_nama_puj_lower:
                    nama = f"{clean_nama} *(Tunggu Pembayaran)*"
    
                hasil += f"{i}/{key}. {nama}<br>"
    
        return hasil
    
    # Tampilkan semua blok
    output = ""
    output += tampilkan_blok("RPA 1 PUJ - WSF (DO)", blok1)
    output += tampilkan_blok("RPA 2 PUJ - WSF (DO)", blok2)
    output += tampilkan_blok("RPB PUJ", blok3)
    st.markdown(output, unsafe_allow_html=True)
