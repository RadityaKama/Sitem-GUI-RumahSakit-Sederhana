import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="daftarumahsakit.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS pasien (
                id_pasien INTEGER PRIMARY KEY AUTOINCREMENT,
                nik TEXT UNIQUE,
                nama TEXT,
                tgl_lahir TEXT,
                alamat TEXT,
                riwayat_penyakit TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS kunjungan (
                id_kunjungan INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pasien INTEGER,
                tgl_kunjungan TEXT,
                no_antrean INTEGER,
                poli_tujuan TEXT,
                status TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS tanda_vital (
                id_tanda_vital INTEGER PRIMARY KEY AUTOINCREMENT,
                id_kunjungan INTEGER,
                berat_badan INTEGER,
                tinggi_badan INTEGER,
                tekanan_darah TEXT,
                suhu_tubuh REAL
            )""",
            """CREATE TABLE IF NOT EXISTS pemeriksaan (
                id_pemeriksaan INTEGER PRIMARY KEY AUTOINCREMENT,
                id_kunjungan INTEGER,
                diagnosis_utama TEXT,
                tindakan_medis TEXT,
                catatan_dokter TEXT,
                resep_obat TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS tagihan (
                id_tagihan INTEGER PRIMARY KEY AUTOINCREMENT,
                id_kunjungan INTEGER,
                total_biaya_jasa REAL,
                total_biaya_obat REAL,
                total_bayar REAL,
                status_bayar BOOLEAN
            )"""
        ]
        for table in tables:
            self.cursor.execute(table)
        self.conn.commit()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

db = DatabaseManager()

class Person:
    def __init__(self, nama):
        self.nama = nama

class Staff(Person):
    def __init__(self, nama, id_staff, jabatan):
        super().__init__(nama)
        self.id_staff = id_staff
        self.jabatan = jabatan

    def get_dashboard_view(self, root):
        frame = tk.Frame(root)
        tk.Label(frame, text=f"Modul {self.jabatan}", font=("Arial", 16, "bold")).pack(pady=10)
        return frame

class Perawat(Staff):
    def __init__(self):
        super().__init__("Suster", "S001", "Perawat")

    def input_tanda_vital(self, id_kunjungan, bb, tb, td, suhu):
        db.execute_query("INSERT INTO tanda_vital (id_kunjungan, berat_badan, tinggi_badan, tekanan_darah, suhu_tubuh) VALUES (?, ?, ?, ?, ?)", 
                         (id_kunjungan, bb, tb, td, suhu))
        db.execute_query("UPDATE kunjungan SET status = 'Menunggu Dokter' WHERE id_kunjungan = ?", (id_kunjungan,))

class Dokter(Staff):
    def __init__(self):
        super().__init__("Dr. Spesialis", "D001", "Dokter")

    def periksa_pasien(self, id_kunjungan, diag, tind, cat, resep):
        db.execute_query("INSERT INTO pemeriksaan (id_kunjungan, diagnosis_utama, tindakan_medis, catatan_dokter, resep_obat) VALUES (?, ?, ?, ?, ?)", 
                         (id_kunjungan, diag, tind, cat, resep))
        db.execute_query("UPDATE kunjungan SET status = 'Menunggu Pembayaran' WHERE id_kunjungan = ?", (id_kunjungan,))

class Administrasi(Staff):
    def __init__(self):
        super().__init__("Admin", "A001", "Administrasi")

    def proses_bayar(self, id_kunjungan, jasa, obat):
        total = jasa + obat
        db.execute_query("INSERT INTO tagihan (id_kunjungan, total_biaya_jasa, total_biaya_obat, total_bayar, status_bayar) VALUES (?, ?, ?, ?, ?)", 
                         (id_kunjungan, jasa, obat, total, 1))
        db.execute_query("UPDATE kunjungan SET status = 'Selesai' WHERE id_kunjungan = ?", (id_kunjungan,))

class Pasien(Person):
    def __init__(self, nik, nama, tgl_lahir, alamat):
        super().__init__(nama)
        self.nik = nik
        self.tgl_lahir = tgl_lahir
        self.alamat = alamat

    def registrasi_mandiri(self, poli_tujuan):
        existing = db.fetch_one("SELECT id_pasien FROM pasien WHERE nik=?", (self.nik,))
        if existing:
            id_pasien = existing[0]
        else:
            db.execute_query("INSERT INTO pasien (nik, nama, tgl_lahir, alamat) VALUES (?, ?, ?, ?)", 
                             (self.nik, self.nama, self.tgl_lahir, self.alamat))
            id_pasien = db.cursor.lastrowid
        
        today_str = datetime.now().strftime("%d-%m-%Y")
        count = db.fetch_one("SELECT COUNT(*) FROM kunjungan WHERE tgl_kunjungan LIKE ?", (f"{today_str}%",))[0]
        
        no_antrean = count + 1
        tgl_skrg = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        db.execute_query("INSERT INTO kunjungan (id_pasien, tgl_kunjungan, no_antrean, poli_tujuan, status) VALUES (?, ?, ?, ?, ?)", 
                         (id_pasien, tgl_skrg, no_antrean, poli_tujuan, "Menunggu Perawat"))
        return no_antrean

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Rumah Sakit Terpadu")
        self.geometry("1100x700")
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_home()

    def show_home(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.container)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame, text="Sistem Informasi Rumah Sakit", font=("Helvetica", 24, "bold")).pack(pady=40)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack()
        
        buttons = [
            ("Registrasi Pasien Mandiri", self.show_registrasi, "#4CAF50"),
            ("Pemeriksaan Perawat", self.show_perawat, "#2196F3"),
            ("Pemeriksaan Dokter", self.show_dokter, "#FF9800"),
            ("Administrasi / Kasir", self.show_admin, "#9C27B0")
        ]
        
        for text, cmd, color in buttons:
            tk.Button(btn_frame, text=text, command=cmd, bg=color, fg="white", font=("Arial", 12), width=30, height=2).pack(pady=10)

    def show_registrasi(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.container)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Button(frame, text="< Kembali ke Menu Utama", command=self.show_home).pack(anchor="w")
        tk.Label(frame, text="Registrasi Mandiri Pasien", font=("Arial", 18, "bold")).pack(pady=20)
        
        form = tk.Frame(frame)
        form.pack()
        
        fields = ["NIK", "Nama Lengkap", "Tgl Lahir (DD-MM-YYYY)", "Alamat"]
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(form, text=field).grid(row=i, column=0, sticky="e", padx=10, pady=5)
            entry = tk.Entry(form, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry
            
        tk.Label(form, text="Poli Tujuan").grid(row=4, column=0, sticky="e", padx=10, pady=5)
        
        poli_list = [
            "Poli Umum", "Poli Penyakit Dalam", "Poli Anak", "Poli Bedah", "Poli Kebidanan dan Kandungan", "Poli Gigi",
            "Poli Jantung", "Poli Saraf", "Poli Paru", "Poli Kulit dan Kelamin", "Poli Mata", "Poli THT", "Poli Ortopedi", "Poli Urologi",
            "Poli Onkologi", "Poli Psikiatri", "Poli Rehabilitasi Medik"
        ]
        
        combo_poli = ttk.Combobox(form, values=poli_list, width=37)
        combo_poli.grid(row=4, column=1, padx=10, pady=5)
        
        def submit():
            p = Pasien(entries["NIK"].get(), entries["Nama Lengkap"].get(), entries["Tgl Lahir (DD-MM-YYYY)"].get(), entries["Alamat"].get())
            try:
                no = p.registrasi_mandiri(combo_poli.get())
                messagebox.showinfo("Berhasil", f"Registrasi Berhasil!\nNomor Antrean Anda: {no}")
                self.show_home()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        tk.Button(frame, text="Dapatkan Nomor Antrean", command=submit, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)

    def show_perawat(self):
        self.setup_staff_view(Perawat(), "Menunggu Perawat", self.form_perawat)

    def show_dokter(self):
        self.setup_staff_view(Dokter(), "Menunggu Dokter", self.form_dokter)

    def show_admin(self):
        self.setup_staff_view(Administrasi(), "Menunggu Pembayaran", self.form_admin)

    def setup_staff_view(self, staff_tugas, status_filter, form_builder):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        frame = tk.Frame(self.container)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        header = tk.Frame(frame)
        header.pack(fill="x")
        tk.Button(header, text="< Menu Utama", command=self.show_home).pack(side="left")
        tk.Label(header, text=f"Dashboard {staff_tugas.jabatan}", font=("Arial", 16, "bold")).pack(side="left", padx=20)
        
        content = tk.Frame(frame)
        content.pack(fill="both", expand=True, pady=10)
        
        tree_frame = tk.Frame(content)
        tree_frame.pack(side="left", fill="y", padx=5)
        
        cols = ("ID", "Pasien", "Poli", "Status")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill="both", expand=True)
        
        data = db.fetch_all(f"""
            SELECT k.id_kunjungan, p.nama, k.poli_tujuan, k.status 
            FROM kunjungan k JOIN pasien p ON k.id_pasien = p.id_pasien 
            WHERE k.status = '{status_filter}'
        """)
        for item in data:
            tree.insert("", "end", values=item)
            
        action_frame = tk.Frame(content, bd=1, relief="solid")
        action_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        tk.Label(action_frame, text="Detail Tindakan", font=("Arial", 12, "bold")).pack(pady=10)
        
        selected_id = tk.IntVar()
        
        def on_select(event):
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                selected_id.set(item['values'][0])
                
        tree.bind("<<TreeviewSelect>>", on_select)
        
        form_builder(action_frame, staff_tugas, selected_id, tree)

    def form_perawat(self, parent, staff, id_var, tree_ref):
        entries = {}
        labels = ["Berat Badan (kg)", "Tinggi Badan (cm)", "Tekanan Darah", "Suhu Tubuh (C)"]
        
        for lb in labels:
            tk.Label(parent, text=lb).pack(anchor="w", padx=10)
            e = tk.Entry(parent)
            e.pack(fill="x", padx=10, pady=2)
            entries[lb] = e
            
        def save():
            if not id_var.get(): return
            staff.input_tanda_vital(id_var.get(), entries["Berat Badan (kg)"].get(), entries["Tinggi Badan (cm)"].get(),
                                    entries["Tekanan Darah"].get(), entries["Suhu Tubuh (C)"].get())
            messagebox.showinfo("Info", "Data Vital Disimpan")
            self.show_perawat()
            
        tk.Button(parent, text="Simpan & Teruskan ke Dokter", command=save, bg="#2196F3", fg="white").pack(pady=20, padx=10, fill="x")

    def form_dokter(self, parent, staff, id_var, tree_ref):
        entries = {}
        labels = ["Diagnosis Utama", "Tindakan Medis", "Catatan Dokter", "Resep Obat"]
        
        for lb in labels:
            tk.Label(parent, text=lb).pack(anchor="w", padx=10)
            e = tk.Entry(parent)
            e.pack(fill="x", padx=10, pady=2)
            entries[lb] = e
            
        def save():
            if not id_var.get(): return
            staff.periksa_pasien(id_var.get(), entries["Diagnosis Utama"].get(), entries["Tindakan Medis"].get(),
                                 entries["Catatan Dokter"].get(), entries["Resep Obat"].get())
            messagebox.showinfo("Info", "Pemeriksaan Selesai")
            self.show_dokter()

        tk.Button(parent, text="Selesai & Teruskan ke Kasir", command=save, bg="#FF9800", fg="white").pack(pady=20, padx=10, fill="x")

    def form_admin(self, parent, staff, id_var, tree_ref):
        entries = {}
        labels = ["Total Biaya Jasa", "Total Biaya Obat"]
        
        for lb in labels:
            tk.Label(parent, text=lb).pack(anchor="w", padx=10)
            e = tk.Entry(parent)
            e.pack(fill="x", padx=10, pady=2)
            entries[lb] = e
            
        def save():
            if not id_var.get(): return
            try:
                jasa = float(entries["Total Biaya Jasa"].get())
                obat = float(entries["Total Biaya Obat"].get())
                staff.proses_bayar(id_var.get(), jasa, obat)
                messagebox.showinfo("Lunas", f"Pembayaran Berhasil. Total: {jasa+obat}")
                self.show_admin()
            except ValueError:
                messagebox.showerror("Error", "Input harus angka")

        tk.Button(parent, text="Proses Pembayaran", command=save, bg="#9C27B0", fg="white").pack(pady=20, padx=10, fill="x")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()