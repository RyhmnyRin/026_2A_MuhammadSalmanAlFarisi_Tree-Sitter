# `cek.py` — Pendeteksi TODO/FIXME, Fungsi Panjang, dan Syntax Error

CLI berbasis `py-tree-sitter` (v0.25+) untuk memindai seluruh file Python (`*.py`) di dalam sebuah folder dan melaporkan:
1. **Komentar `TODO` atau `FIXME`** beserta nama file dan nomor baris.
2. **Fungsi dengan panjang lebih dari 30 baris** (`end_point[0] - start_point[0] + 1 > 30`).
3. **File yang mengandung syntax error** (`tree.root_node.has_error`) beserta nomor baris pertama yang bermasalah (`is_error` / `is_missing`).

---

## 1. Cara Memasang Dependensi

Pastikan Python 3.10+ sudah terpasang, lalu jalankan:

```bash
pip install tree-sitter tree-sitter-python
```

---

## 2. Cara Menjalankan

```bash
python cek/cek.py <path_folder>
```

Contoh menjalankan pada folder uji lokal:

```bash
python cek/cek.py cek/uji
```

Contoh menjalankan pada repositori open source nyata (misalnya hasil `git clone https://github.com/psf/requests.git`):

```bash
python cek/cek.py ../repo_uji_requests
```

### Catatan Perhitungan Fungsi
- Query `(function_definition name: (identifier) @nama) @fungsi` menghitung **semua definisi fungsi** di dalam file, termasuk fungsi tingkat modul, **method di dalam kelas** (seperti `__init__`, `send`, dll.), maupun **fungsi bersarang (nested function)**.
- Direktori `venv/`, `.venv/`, `.git/`, dan `node_modules/` otomatis dilewati agar pemindaian tetap cepat pada repositori besar.

---

## 3. Contoh Output

### A. Output pada Folder Uji Lokal (`cek/uji`)

```text
cek\uji\uji_error.py:5: ditemukan syntax error pada file
cek\uji\uji_panjang.py:5: fungsi 'proses_transaksi_panjang' terlalu panjang (35 baris)
cek\uji\uji_todo.py:1: # TODO: tambahkan validasi input kosong
cek\uji\uji_todo.py:3: # FIXME: tarif pajak masih hardcode
```

### B. Output pada Repositori Open Source Nyata (`psf/requests`)

```text
repo_uji_requests\tests\test_lowlevel.py:127: fungsi 'test_digestauth_401_count_reset_on_redirect' terlalu panjang (63 baris)
repo_uji_requests\tests\test_testserver.py:97: # TODO: figure out why this sometimes fails when using pytest-xdist.
repo_uji_requests\src\requests\adapters.py:715: # TODO: Remove this in 3.0.0: see #2811
repo_uji_requests\src\requests\adapters.py:85: fungsi '_urllib3_request_context' terlalu panjang (35 baris)
repo_uji_requests\src\requests\adapters.py:634: fungsi 'send' terlalu panjang (115 baris)
repo_uji_requests\src\requests\api.py:24: fungsi 'request' terlalu panjang (48 baris)
repo_uji_requests\src\requests\auth.py:157: fungsi 'build_digest_header' terlalu panjang (110 baris)
repo_uji_requests\src\requests\hooks.py:29: # TODO: response is the only one
repo_uji_requests\src\requests\models.py:687: # TODO: can be fixed by flipping the conditionals
repo_uji_requests\src\requests\models.py:1016: # TODO: remove cast after iter_lines rewrite
repo_uji_requests\src\requests\sessions.py:186: fungsi 'resolve_redirects' terlalu panjang (122 baris)
repo_uji_requests\src\requests\_types.py:60: # TODO: move to collections.abc when Python >= 3.12
repo_uji_requests\src\requests\_types.py:61: # TODO: move to typing when Python >= 3.13
```

---

## 4. Verifikasi Manual pada 2 File Acak (`psf/requests`)

1. **File 1: `src/requests/api.py`**
   - **Laporan `cek.py`**: `baris 24: fungsi 'request' terlalu panjang (48 baris)`
   - **Pengecekan manual**: Fungsi `def request(...)` dimulai pada **baris 24** dan berakhir pada **baris 71** (`return session.request(...)`). Selisih baris: `71 - 24 + 1 = 48 baris` (**Cocok**). Fungsi lain di file yang sama (`get`, `options`, `head`, `post`, `put`, `patch`, `delete`) semuanya ≤ 30 baris sehingga tidak dilaporkan.

2. **File 2: `src/requests/adapters.py`**
   - **Laporan `cek.py`**:
     - `baris 715: # TODO: Remove this in 3.0.0: see #2811`
     - `baris 85: fungsi '_urllib3_request_context' terlalu panjang (35 baris)`
   - **Pengecekan manual**:
     - Pada **baris 715** terdapat tepat komentar `# TODO: Remove this in 3.0.0: see #2811` (**Cocok**).
     - Fungsi `def _urllib3_request_context(...)` dimulai pada **baris 85** dan berakhir pada **baris 119** (`return host_params, pool_kwargs`). Selisih baris: `119 - 85 + 1 = 35 baris` (**Cocok**).
