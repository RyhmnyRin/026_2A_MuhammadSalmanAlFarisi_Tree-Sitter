def fungsi_pendek(x):
    return x + 1


def proses_transaksi_panjang(daftar_item):
    total = 0
    diskon = 0
    pajak = 0
    biaya_admin = 2500
    catatan = []

    for item in daftar_item:
        nama = item.get("nama", "tanpa_nama")
        harga = item.get("harga", 0)
        jumlah = item.get("jumlah", 1)
        subtotal = harga * jumlah
        total += subtotal
        catatan.append(f"{nama}: {subtotal}")

    if total > 1000000:
        diskon = total * 0.10
    elif total > 500000:
        diskon = total * 0.05
    else:
        diskon = 0

    setelah_diskon = total - diskon
    pajak = setelah_diskon * 0.11
    grand_total = setelah_diskon + pajak + biaya_admin

    hasil = {
        "total_awal": total,
        "diskon": diskon,
        "pajak": pajak,
        "biaya_admin": biaya_admin,
        "grand_total": grand_total,
        "rincian": catatan,
    }
    return hasil
