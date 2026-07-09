import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Dashboard Lingkar Cerita", layout="wide", page_icon="📖")

st.title("📖 Dashboard Komunitas Lingkar Cerita")
st.subheader("Monitoring Konsistensi Membaca & Tren Empati AI")

# --- KONEKSI DATA (Membaca Google Sheets Publik via CSV) ---
# CARA MENDAPATKAN URL: Di Google Sheets -> File -> Share -> Publish to web -> Pilih format 'Commas-separated values (.csv)'
# Ganti URL di bawah ini dengan link CSV hasil Publish to Web kamu
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRefCDk21THyWTZxfyzVeOam0ads4HD2m_GySetpi3uIoSLR7YAITUXjfAQSMXLAAEtXvufxrKuwuBe/pub?gid=1074415517&single=true&output=csv"

@st.cache_data(ttl=600) # Data di-cache selama 10 menit agar loading cepat
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # Standardisasi nama kolom agar cocok dengan setup Langkah 1
        df.columns = ['Timestamp', 'Nama', 'Judul Buku', 'Halaman', 'Refleksi', 'Skor Empati', 'Feedback AI']
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Skor Empati'] = pd.to_numeric(df['Skor Empati'], errors='coerce')
        df['Halaman'] = pd.to_numeric(df['Halaman'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets: {e}")
        return None

df = load_data()

if df is not None:
    # --- ROW 1: METRIK UTAMA (KPI) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        total_laporan = len(df)
        st.metric(label="Total Laporan Bacaan", value=total_laporan)
    with col2:
        total_halaman = int(df['Halaman'].sum())
        st.metric(label="Total Halaman Dibaca", value=f"{total_halaman} Hlm")
    with col3:
        rata_skor_empati = df['Skor Empati'].dropna().mean()
        st.metric(label="Rata-rata Skor Empati AI", value=f"{rata_skor_empati:.1f}/100" if not pd.isna(rata_skor_empati) else "N/A")

    st.markdown("---")

    # --- ROW 2: GRAFIK VISUALISASI ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("🔥 Konsistensi Membaca (Jumlah Laporan per Anggota)")
        # Menghitung seberapa sering anggota mengisi form
        konsistensi_df = df['Nama'].value_counts().reset_index()
        konsistensi_df.columns = ['Nama', 'Jumlah Laporan']
        fig_bar = px.bar(konsistensi_df, x='Nama', y='Jumlah Laporan', 
                         labels={'Jumlah Laporan': 'Frekuensi Mengisi Form'},
                         color='Jumlah Laporan', color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.subheader("🧠 Tren Empati Longitudinal (Pendekatan Psikologi)")
        # Menampilkan perkembangan skor empati anggota dari waktu ke waktu
        df_sorted = df.dropna(subset=['Skor Empati']).sort_values('Timestamp')
        if not df_sorted.empty:
            fig_line = px.line(df_sorted, x='Timestamp', y='Skor Empati', color='Nama', markers=True,
                               labels={'Skor Empati': 'Skor Empati Afektif AI', 'Timestamp': 'Tanggal Lapor'},
                               title="Perkembangan Keterlibatan Emosional Anggota")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Grafik tren empati akan muncul setelah AI memproses skor di Google Sheets.")

    # --- ROW 3: DETAIL DATA & FEEDBACK AI ---
    st.markdown("---")
    st.subheader("📄 Catatan Bacaan Terbaru & Feedback AI")
    
    # Menampilkan tabel data yang rapi untuk dipantau Admin
    view_df = df[['Timestamp', 'Nama', 'Judul Buku', 'Halaman', 'Skor Empati', 'Feedback AI']].sort_values('Timestamp', ascending=False)
    st.dataframe(view_df, use_container_width=True)

else:
    st.warning("Silakan hubungkan URL Google Sheets kamu terlebih dahulu pada variabel SHEET_CSV_URL di dalam kode.")