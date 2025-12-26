# Sistem Informasi Rumah Sakit Sederhana

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![GUI](https://img.shields.io/badge/Interface-Tkinter-green.svg)
![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)

Aplikasi desktop sederhana berbasis **Python** dan **Tkinter** untuk manajemen alur pasien rumah sakit, mulai dari pendaftaran mandiri hingga penyelesaian administrasi pembayaran. Aplikasi ini menggunakan **SQLite** sebagai penyimpanan data lokal.

## Daftar Isi
- [Fitur Utama](#-fitur-utama)
- [Struktur Program](#-struktur-program)
- [Alur Kerja Sistem](#-alur-kerja-sistem)
- [Prasyarat](#-prasyarat)
- [Cara Menjalankan](#-cara-menjalankan)
- [Skema Database](#-skema-database)

## Fitur Utama
1.  **Pendaftaran Pasien Mandiri**: 
    - Validasi NIK (mencegah duplikasi data pasien).
    - Pemilihan Poli Tujuan (Umum, Spesialis, dan Khusus).
    - Pembuatan nomor antrean otomatis berdasarkan tanggal.
2.  **Modul Perawat (Triage)**: 
    - Input tanda vital (Tinggi, Berat, Tekanan Darah, Suhu).
    - Update status antrean ke "Menunggu Dokter".
3.  **Modul Dokter (Pemeriksaan)**: 
    - Input Diagnosis, Tindakan, Catatan, dan Resep Obat.
    - Update status antrean ke "Menunggu Pembayaran".
4.  **Modul Administrasi (Kasir)**: 
    - Perhitungan total biaya (Jasa + Obat).
    - Penyelesaian status kunjungan pasien.
5.  **Penyimpanan Data Persisten**: Menggunakan SQLite, data tidak hilang saat aplikasi ditutup.

## Struktur Program
Aplikasi ini dibangun menggunakan konsep **Object-Oriented Programming (OOP)**:

- **`DatabaseManager`**: Menangani koneksi SQLite, inisialisasi tabel, dan eksekusi query.
- **`Person`**: *Base Class* untuk semua entitas manusia.
- **`Pasien` (Inherits Person)**: Menangani logika registrasi dan data demografis.
- **`Staff` (Inherits Person)**: *Parent Class* untuk karyawan RS.
  - **`Perawat`**: Logika input vital sign.
  - **`Dokter`**: Logika pemeriksaan medis.
  - **`Administrasi`**: Logika pembayaran.
- **`MainApp` (tk.Tk)**: Mengatur navigasi GUI dan perpindahan antar modul.

## Alur Kerja Sistem
Sistem ini menggunakan *State Management* sederhana pada kolom `status` di tabel `kunjungan`:

1.  **Pasien Datang** ➡️ Registrasi ➡️ Status: `Menunggu Perawat`
2.  **Perawat** ➡️ Input Tanda Vital ➡️ Status: `Menunggu Dokter`
3.  **Dokter** ➡️ Pemeriksaan & Resep ➡️ Status: `Menunggu Pembayaran`
4.  **Kasir** ➡️ Proses Bayar ➡️ Status: `Selesai`

## Prasyarat
- Python 3.x terinstall di komputer.
- Pustaka bawaan Python (tidak perlu install via PIP):
  - `tkinter`
  - `sqlite3`
  - `datetime`

## Cara Menjalankan

1.  **Clone repositori ini** (atau download zip):
    ```bash
    git clone [https://github.com/username-anda/sistem-rumah-sakit.git](https://github.com/username-anda/sistem-rumah-sakit.git)
    cd sistem-rumah-sakit
    ```

2.  **Jalankan aplikasi**:
    ```bash
    python main.py
    ```
    *(Pastikan nama file utamanya adalah `main.py` atau sesuaikan dengan nama file kamu)*

3.  **Database**:
    File `daftarumahsakit.db` akan otomatis dibuat di folder yang sama saat pertama kali dijalankan.

## Skema Database
Aplikasi ini otomatis membuat tabel berikut:
- **`pasien`**: Menyimpan NIK, Nama, Tgl Lahir, Alamat.
- **`kunjungan`**: Menyimpan ID Pasien, Tanggal, No Antrean, Poli, Status.
- **`tanda_vital`**: Menyimpan data pemeriksaan fisik perawat.
- **`pemeriksaan`**: Menyimpan diagnosis dan resep dokter.
- **`tagihan`**: Menyimpan rincian biaya dan status bayar.

## Poli yang Tersedia
Mencakup Poli Utama, Spesialis, dan Khusus, antara lain:
- Poli Umum, Gigi, Penyakit Dalam, Anak.
- Poli Jantung, Saraf, Paru, Mata, THT.
- Poli Onkologi, Psikiatri, Rehabilitasi Medik, dll.

---
**Disclaimer**: Aplikasi ini dibuat untuk tujuan pembelajaran dan simulasi sistem informasi manajemen rumah sakit sederhana.
