# Proposal Draf Proyek Tree-sitter: Guardrail Keamanan & Standar Kode Backend Express.js

**Nama**: Muhammad Salman Al Farisi  
**NIM / Kelas**: 026 / 2A  

---

## 1. Judul
**JS-Guardrail: Linter Deterministik Berbasis Tree-sitter untuk Deteksi Kebocoran Log dan Potensi SQL Injection pada Aplikasi Web Enterprise (Node.js / Express.js)**

## 2. Masalah
Dalam pengembangan aplikasi web enterprise berbasis Node.js/Express.js yang dikerjakan oleh banyak developer (maupun dibantu AI coding assistant), tiga kesalahan sering lolos ke tahap *code review*: (1) tertinggalnya `console.log(...)` di kode produksi yang berisiko membocorkan data sensitif ke stdout, (2) pembentukan query SQL menggunakan penggabungan string / *template literal* (`db.query(\`SELECT ... \${id}\`)`) yang membuka celah **SQL Injection**, dan (3) *route handler* `async` yang tidak membungkus operasi database di dalam `try/catch`. Masalah ini dialami oleh **tim developer backend, code reviewer, dan tim DevSecOps**. Pendekatan berbasis **regex atas teks mentah akan gagal** karena regex tidak dapat membedakan antara pemanggilan fungsi `console.log(...)` yang nyata dengan teks `"console.log"` di dalam string/komentar, serta sulit mengenali ekspresi `template_substitution` (`${...}`) yang bersarang multi-baris di dalam argumen fungsi query database.

## 3. Kenapa Tidak Cukup dengan AI Saja
Meminta LLM/AI me-review seluruh kode pada setiap *commit* atau *pull request* di repositori enterprise berukuran ribuan file memakan biaya token yang besar, membutuhkan waktu puluhan detik hingga menit, serta bersifat **probabilistik** (hasil review bisa berubah-ubah atau mengalami *false negative* antar eksekusi). Sebaliknya, tool berbasis **tree-sitter** bersifat **100% deterministik** (input pohon yang sama selalu menghasilkan laporan yang sama), berbiaya komputasi hampir nol, mampu memindai ribuan file per detik, dan dapat dipasang langsung sebagai *quality gate* otomatis di pipeline CI/CD maupun sebagai *pre-commit hook* sebelum kode di-merge.

## 4. Bahasa dan Framework Target beserta Grammar Tree-sitter
- **Bahasa & Framework Target**: JavaScript (ES6+) pada backend **Node.js / Express.js**.
- **Grammar Tree-sitter**: Paket resmi **`tree-sitter-javascript`** yang tersedia di PyPI (`pip install tree-sitter tree-sitter-javascript`).

## 5. Contoh Kode yang Harus Terdeteksi vs Tidak Boleh Ikut Terdeteksi

**Harus Terdeteksi (Melanggar Aturan):**
```javascript
// Aturan 1: Pemanggilan console.log langsung di kode produksi
console.log(user.password);

// Aturan 2: Query SQL menggunakan template literal dengan interpolasi variabel (${...})
db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);
```

**Tidak Boleh Ikut Terdeteksi (Aman / Valid):**
```javascript
// Teks "console.log" di dalam string atau pemakaian logger resmi
const panduan = "Jangan gunakan console.log di kode produksi";
logger.info("User berhasil autentikasi");

// Parameterized query atau template literal statis tanpa interpolasi variabel
db.query("SELECT * FROM users WHERE id = ?", [req.params.id]);
db.query(`SELECT id, username FROM users`);
```

## 6. Rancangan Query S-expression (Sudah Diuji dengan `tree-sitter-javascript`)

**Aturan 1 — Deteksi pemanggilan `console.log(...)`:**
```scheme
(call_expression
  function: (member_expression
    object: (identifier) @obj
    property: (property_identifier) @prop)
  arguments: (arguments) @args
  (#eq? @obj "console")
  (#eq? @prop "log")) @temuan
```

**Aturan 2 — Deteksi potensi SQL Injection pada `.query(...)` dengan interpolasi `${...}`:**
```scheme
(call_expression
  function: (member_expression
    property: (property_identifier) @method)
  arguments: (arguments
    (template_string
      (template_substitution)))
  (#eq? @method "query")) @sqli
```

## 7. Bentuk Output
Tool dijalankan melalui CLI (`python js_guardrail.py <path_repo> [--json]`) dan menghasilkan:
1. **Laporan Terminal** berformat `file:baris:kolom: [KODE_ATURAN] pesan pelanggaran beserta cuplikan kode` (mengembalikan *exit code* `1` jika ditemukan pelanggaran di CI).
2. **File JSON (`report.json`)** yang merangkum daftar temuan untuk diintegrasikan ke komentar otomatis pada GitHub Pull Request.

## 8. Cara Evaluasi
- **Repositori Uji**: Menguji tool pada 1–2 repositori aplikasi Express.js open source di GitHub serta satu modul uji berisi pasangan kasus positif (*true positive*) dan kasus pengecoh (*true negative* seperti komentar, string literal, dan *parameterized query*).
- **Metode Pengecekan**: Mengambil minimal **20 temuan secara acak** dari hasil eksekusi pada repositori uji, memeriksa kode sumber aslinya secara manual baris demi baris, lalu menghitung tingkat akurasi (*precision*) dan memastikan tidak ada *false positive* pada string/komentar.

## 9. Rencana Kerja per Minggu (5 Pertemuan) dan Risiko
- **Minggu 1**: Finalisasi spesifikasi 3 aturan linter (larangan `console.log`, SQL injection pada *template string*, dan *async route handler* Express tanpa `try/catch`) beserta eksplorasi CST `tree-sitter-javascript`.
- **Minggu 2**: Implementasi dan pengujian query S-expression untuk Aturan 1 dan Aturan 2 beserta *test suite* kasus positif/negatif.
- **Minggu 3**: Implementasi Aturan 3 (pemeriksaan `try_statement` di dalam body *async callback* Express route) dan pembuatan CLI utama.
- **Minggu 4**: Penambahan dukungan output JSON, integrasi contoh workflow GitHub Actions CI, dan pengujian pada repositori Express.js nyata.
- **Minggu 5**: Evaluasi manual terhadap ≥20 temuan, penyempurnaan dokumentasi `README.md`, dan demo akhir.
- **Risiko & Mitigasi**: Variasi cara penulisan pemanggilan query database atau route handler di JavaScript cukup beragam (misal `pool.query`, `conn.execute`, atau *arrow function* vs *function declaration*). Mitigasinya adalah membatasi skop secara jelas pada pola standar Express.js + driver database umum (`mysql2`/`pg`) dan menggunakan predikat `#match?` pada nama method.
