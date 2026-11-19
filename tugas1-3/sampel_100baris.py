import os
import json
from pathlib import Path
from datetime import datetime


class Tiket:
    """Representasi tiket layanan pelanggan."""

    def __init__(self, kode, judul, prioritas, status="open"):
        self.kode = kode
        self.judul = judul
        self.prioritas = prioritas
        self.status = status
        self.dibuat = datetime.now().isoformat()

    def ringkasan(self):
        return f"[{self.kode}] ({self.status}) {self.judul} - P{self.prioritas}"

    def tutup(self, catatan=""):
        self.status = "closed"
        if catatan:
            print(f"Tiket {self.kode} ditutup: {catatan}")
        else:
            print(f"Tiket {self.kode} ditutup.")


def buat_tiket_awal():
    daftar = [
        Tiket("TK-01", "Gagal login SSO", 1, "open"),
        Tiket("TK-02", "Ekspor CSV lambat", 2, "pending"),
        Tiket("TK-03", "Typo pada halaman bantuan", 3, "open"),
        Tiket("TK-04", "Timeout integrasi pembayaran", 1, "open"),
    ]
    return daftar


def hitung_berdasarkan_status(daftar_tiket, target_status):
    total = 0
    for tiket in daftar_tiket:
        if tiket.status == target_status:
            total += 1
    return total


def cari_prioritas_tinggi(daftar_tiket, batas=1):
    hasil = []
    for tiket in daftar_tiket:
        if tiket.prioritas <= batas and tiket.status != "closed":
            hasil.append(tiket)
    return hasil


def urutkan_tiket(daftar_tiket, berdasarkan_prioritas=True):
    if berdasarkan_prioritas:
        return sorted(daftar_tiket, key=lambda t: t.prioritas)
    return sorted(daftar_tiket, key=lambda t: t.kode)


def simpan_ke_json(daftar_tiket, path_tujuan):
    data = []
    for tiket in daftar_tiket:
        data.append({
            "kode": tiket.kode,
            "judul": tiket.judul,
            "prioritas": tiket.prioritas,
            "status": tiket.status,
            "dibuat": tiket.dibuat,
        })
    Path(path_tujuan).write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Data tersimpan ke {path_tujuan}")


def muat_dari_json(path_sumber):
    p = Path(path_sumber)
    if not p.exists():
        print("File belum ditemukan, membuat daftar kosong.")
        return []
    isi = json.loads(p.read_text(encoding="utf-8"))
    hasil = []
    for item in isi:
        t = Tiket(
            item["kode"],
            item["judul"],
            item["prioritas"],
            item.get("status", "open"),
        )
        hasil.append(t)
    return hasil


def cetak_laporan(daftar_tiket):
    print("=== Laporan Tiket ===")
    print("Total tiket:", len(daftar_tiket))
    print("Open:", hitung_berdasarkan_status(daftar_tiket, "open"))
    print("Pending:", hitung_berdasarkan_status(daftar_tiket, "pending"))
    print("Closed:", hitung_berdasarkan_status(daftar_tiket, "closed"))
    for tiket in urutkan_tiket(daftar_tiket):
        print(" -", tiket.ringkasan())


def jalankan_demo():
    folder = Path(os.getcwd())
    print("Direktori kerja:", folder)
    tiket_list = buat_tiket_awal()
    kritis = cari_prioritas_tinggi(tiket_list, batas=1)
    print("Jumlah tiket kritis:", len(kritis))
    if tiket_list:
        tiket_list[0].tutup("Sudah diperbaiki pada rilis patch.")
    cetak_laporan(tiket_list)


if __name__ == "__main__":
    jalankan_demo()
