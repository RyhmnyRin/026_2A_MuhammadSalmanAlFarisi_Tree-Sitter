# Laporan Praktikum Tree-sitter (Programming Language Pragmatics)

**Nama**: Muhammad Salman Al Farisi  
**NIM / Kelas**: 026 / 2A  
**Repositori**: `026_2A_MuhammadSalmanAlFarisi_Tree-Sitter`

---

## 1. Penjelasan Singkat & Hasil Tiap Tugas

### Tugas 1 — Membaca Pohon (`tugas1-3/t1.py` & `output_t1.txt`)
- **Tujuan**: Membangun model mental *"kode adalah pohon"* dengan mem-parse kode Python dan membaca Concrete Syntax Tree (CST) dalam bentuk S-expression.
- **Perbandingan Pohon Perkiraan vs Hasil Parse**:
  1. **Potongan 1 (Fungsi `def sapa(nama): return nama`)**:
     - *Perkiraan awal*: `(module (function_definition (identifier) (parameters (identifier)) (return_statement (identifier))))`
     - *Hasil sebenarnya*: `(module (function_definition name: (identifier) parameters: (parameters (identifier)) body: (block (return_statement (identifier)))))`
     - *Perbedaan*: Isi fungsi dibungkus di dalam node `block` pada field `body:`, dan setiap child penting memiliki label field (`name:`, `parameters:`, `body:`).
  2. **Potongan 2 (`if x > 0: y = 1 else: y = 2`)**:
     - *Perkiraan awal*: `(module (if_statement (comparison_operator (identifier) (integer)) (block ...) (else_clause (block ...))))`
     - *Hasil sebenarnya*: `(module (if_statement condition: (comparison_operator (identifier) (integer)) consequence: (block (expression_statement (assignment left: (identifier) right: (integer)))) alternative: (else_clause body: (block (expression_statement (assignment left: (identifier) right: (integer)))))))`
     - *Perbedaan*: Setiap assignment dibungkus oleh `expression_statement`, dan cabang `if`/`else` diberi field `condition:`, `consequence:`, serta `alternative:`.
  3. **Potongan 3 (Kelas `Kucing` dengan method `suara(self)`)**:
     - *Perkiraan awal*: `(module (class_definition (identifier) (block (function_definition ... (string)))))`
     - *Hasil sebenarnya*: Node `string` di `tree-sitter-python` memiliki child bernama `(string (string_start) (string_content) (string_end))`.
- **Perbedaan `children` vs `named_children` & Node Anonim**:
  - Pada node `function_definition` (`def sapa(nama): ...`), `func_node.children` berisi **5 node**: `['def', 'identifier', 'parameters', ':', 'block']`, sedangkan `func_node.named_children` hanya berisi **3 node bernama**: `['identifier', 'parameters', 'block']`.
  - **Node anonim yang tersembunyi dari S-expression**: `'def'`, `':'`, serta `'('` dan `')'` di dalam node `parameters`.
- **Error Recovery**:
  - Ketika `:` dihapus (`def sapa(nama)`), parser tetap menghasilkan pohon dengan menyisipkan node `(ERROR (identifier) (parameters (identifier)) (identifier))`. Saat `)` dihapus, bagian parameter yang rusak dibungkus dalam `(ERROR (identifier) (identifier))` sementara `(return_statement (identifier))` setelahnya tetap berhasil dikenali.
- **Tangkapan Layar Hasil Tugas 1**:
  - ![Hasil Tugas 1](screenshots/tugas1.png)

---

### Tugas 2 — Penjelajah Node (`tugas1-3/jelajah.py` & `output_jelajah.txt`)
- **Cara Kerja**: Menelusuri CST secara rekursif preorder (DFS) menggunakan `enumerate(node.children)`, melewati node anonim (`if child.is_named:`), mengambil nama field melalui `node.field_name_for_child(i)`, lalu mencetak indentasi sesuai kedalaman beserta `tipe [baris:kolom]`.
- **Hasil Uji**:
  - Pada `kecil.py` (`x = 1`), output tercetak sesuai spesifikasi modul (`module [1:0]` -> `expression_statement` -> `assignment` -> `left: identifier [1:0]` & `right: integer [1:4]`).
  - Pada `sampel_100baris.py` (**114 baris** kode Python nyata), `jelajah.py` menghasilkan **712 baris** pohon node bernama lengkap di `tugas1-3/output_jelajah.txt`.
- **Tangkapan Layar Hasil Tugas 2**:
  - ![Hasil Tugas 2](screenshots/tugas2.png)

---

### Tugas 3 — Query Pertama (`tugas1-3/q.py`, `*.scm`, & `output_t3.txt`)
- **Cara Kerja**: `q.py` menerima path file kode Python (`sys.argv[1]`) dan file query `.scm` (`sys.argv[2]`). Untuk query yang membutuhkan pasangan nama fungsi dan parameter (`fungsi.scm`), digunakan `QueryCursor(Query(PY, pola)).matches(tree.root_node)` dan `named_child_count` pada `@params`. Untuk query lainnya digunakan `.captures(tree.root_node)`.
- **Verifikasi Manual pada `sampel_100baris.py` (114 baris)**:
  1. **Query 1 (`fungsi.scm`)**: Menemukan seluruh **11 fungsi/method** beserta jumlah parameternya (`__init__`: 5, `ringkasan`: 1, `tutup`: 2, `buat_tiket_awal`: 0, `hitung_berdasarkan_status`: 2, `cari_prioritas_tinggi`: 2, `urutkan_tiket`: 2, `simpan_ke_json`: 2, `muat_dari_json`: 1, `cetak_laporan`: 1, `jalankan_demo`: 0) — cocok 100% dengan hitungan manual.
  2. **Query 2 (`print.scm`)**: Menemukan seluruh **12 pemanggilan `print(...)`** menggunakan predikat `(#eq? @fn "print")`.
  3. **Query 3 (`import.scm`)**: Berdasarkan hasil inspeksi `jelajah.py`, dibuat pola untuk `import_statement` (baik `dotted_name` langsung maupun `aliased_import`) dan `import_from_statement` (`module_name: (dotted_name)`). Terdeteksi tepat **4 modul** di `sampel_100baris.py` (`os`, `json`, `pathlib`, `datetime`) dan **2 modul** di `t1.py` (`tree_sitter_python`, `tree_sitter`).
- **Tangkapan Layar Hasil Tugas 3**:
  - ![Hasil Tugas 3](screenshots/tugas3.png)

---

### Tugas 4 — Grammar DSL Filter (`tree-sitter-filter/grammar.js` & `test/corpus/dasar.txt`)
- **Pembangunan Inkremental**:
  - Dibangun bertahap mulai dari grammar perbandingan paling kecil (`status = "open"`), langkah **4a** (operator `!=`, `>`, `<`, `>=`, `<=` & `number`), **4b** (`_expr`, `and_expression`, dan `word: $ => $.identifier`), **4c** (`or_expression` & prioritas `prec.left`), **4d** (`parenthesized`), **4e** (`not_expression` dengan `prec(3, ...)` & `boolean`), **4f** (label `field(...)`), hingga penambahan node baru **`in_expression`** dan operator **`contains`**.
  - **Prioritas Operator**: `not_expression` (`prec 3`) > `and_expression` (`prec.left 2`) > `or_expression` (`prec.left 1`), sehingga `a = 1 or b = 2 and c = 3` mengelompok sebagai `a = 1 or (b = 2 and c = 3)`.
- **Hasil Pengujian (`tree-sitter test`)**:
  - Seluruh **8 kasus uji corpus** di `test/corpus/dasar.txt` lulus **100.00%** (mencakup string, number, boolean, prioritas `and`/`or`, tanda kurung, `not`, `in_expression` dengan 3 nilai, dan `contains`).
- **Tangkapan Layar Hasil Tugas 4**:
  - ![Hasil Tugas 4](screenshots/tugas4.png)

---

### Tugas 5 — Highlight untuk DSL Filter (`tree-sitter-filter/queries/highlights.scm`)
- **Konfigurasi**: Menjalankan `tree-sitter init-config` dan mendaftarkan folder induk `026_2A_MuhammadSalmanAlFarisi_Tree-Sitter` pada `parser-directories` di `config.json`. Di `tree-sitter.json`, diatur `"file-types": ["filter"]` dan `"highlights": "queries/highlights.scm"`.
- **Pola Highlight**: Menangkap kata kunci `["and" "or" "not" "in" "contains"] @keyword`, operator `["=" "!=" ">" "<" ">=" "<="] @operator`, literal `(string) @string`, `(number) @number`, `(boolean) @constant.builtin`, serta nama field `(comparison field: (identifier) @property)` dan `(in_expression field: (identifier) @property)`.
- **Tangkapan Layar Hasil Tugas 5**:
  - ![Hasil Tugas 5](screenshots/tugas5.png)

---

### Tugas 6 — Mini Proyek `cek.py` (`cek/cek.py` & `cek/README.md`)
- **Tiga Fitur Utama**:
  1. Deteksi komentar `TODO`/`FIXME` dengan query `((comment) @c (#match? @c "TODO|FIXME"))`.
  2. Deteksi fungsi > 30 baris dengan query `(function_definition name: (identifier) @nama) @fungsi` dan perhitungan `end_point[0] - start_point[0] + 1 > 30`.
  3. Deteksi file dengan syntax error melalui `tree.root_node.has_error` dan penelusuran rekursif mencari node pertama yang `is_error` atau `is_missing`.
- **Uji pada Repositori Open Source Nyata (`psf/requests`) & Verifikasi Manual 2 File Acak**:
  1. **`src/requests/api.py`**: Dilaporkan `baris 24: fungsi 'request' terlalu panjang (48 baris)`. Dicek manual: `def request` berada di baris 24–71 (`71 - 24 + 1 = 48 baris`, cocok).
  2. **`src/requests/adapters.py`**: Dilaporkan `baris 715: # TODO: Remove this in 3.0.0: see #2811` dan `baris 85: fungsi '_urllib3_request_context' terlalu panjang (35 baris)`. Dicek manual: komentar `# TODO` tepat di baris 715, dan fungsi `_urllib3_request_context` berada di baris 85–119 (`119 - 85 + 1 = 35 baris`, cocok).
- **Tangkapan Layar Hasil Tugas 6**:
  - ![Hasil Tugas 6](screenshots/tugas6.png)

---

## 2. Kendala dan Cara Mengatasinya

1. **Indeks `field_name_for_child(i)` di Tugas 2**:
   - *Kendala*: Jika melakukan iterasi pada `node.named_children`, indeks `i` tidak sesuai dengan posisi child sebenarnya sehingga `field_name_for_child(i)` mengembalikan `None` atau field yang salah.
   - *Solusi*: Melakukan iterasi `for i, child in enumerate(node.children):` pada seluruh child, lalu menyaring `if child.is_named:` di dalam loop.
2. **Error `Unresolved conflict` saat Menambahkan `or_expression` di Tugas 4 Langkah 4c**:
   - *Kendala*: Saat `or_expression: $ => seq($._expr, "or", $._expr)` ditulis tanpa `prec.left`, `tree-sitter generate` menolak grammar dengan pesan:
     `Unresolved conflict for symbol sequence: _expr 'or' _expr • 'or' …`
   - *Solusi*: Menambahkan asosiativitas kiri dan tingkat prioritas `prec.left(1, ...)` pada `or_expression` dan `prec.left(2, ...)` pada `and_expression`.
3. **Perbedaan Format `grammar.js` pada `tree-sitter-cli` v0.27.2**:
   - *Kendala*: `package.json` hasil `tree-sitter init` memakai `"type": "module"`, sehingga sintaks CommonJS `module.exports = grammar({...})` dari contoh lama tidak sesuai dengan ES Module.
   - *Solusi*: Menggunakan sintaks `export default grammar({...})` pada `grammar.js`.

---

## 3. Catatan Penggunaan AI

Selama praktikum, AI coding agent digunakan sebagai asisten pendamping dengan verifikasi bertahap pada setiap langkah:

| Tugas | 1. Apa yang Diminta ke AI | 2. Kesalahan / Kekurangan Hasil AI yang Ditemukan | 3. Bukti Verifikasi & Perbaikan |
| --- | --- | --- | --- |
| **Tugas 1 & 2** | Membuat skrip `t1.py` dan `jelajah.py` serta menyimpan output eksekusinya ke file `output_t1.txt` di Windows PowerShell. | Saat menyimpan output pertama kali, AI menggunakan operator redirect PowerShell `python t1.py > output_t1.txt` yang di Windows PowerShell menghasilkan encoding **UTF-16LE** (`b'\xff\xfe...'`), sehingga Git menganggap file `.txt` sebagai file biner. | Dibuktikan dengan memeriksa 4 byte awal file (`b'\xff\xfe=\x00'`) dan `git diff`. Diperbaiki dengan menulis file output secara eksplisit menggunakan encoding `utf-8` tanpa BOM. |
| **Tugas 3** | Menulis query `import.scm` untuk mengekstrak nama modul dari semua pernyataan `import` dan `from ... import ...`. | Rancangan pola awal yang hanya menangkap `(import_statement name: (dotted_name) @modul_import)` gagal menangkap import yang memakai alias (`import tree_sitter_python as tspython` pada `t1.py`) karena di pohon sintaks node tersebut dibungkus oleh `aliased_import`. | Dibuktikan dengan menjalankan `jelajah.py` pada `t1.py` yang memperlihatkan struktur `import_statement -> name: aliased_import -> name: dotted_name`. Ditambahkan pola `(import_statement name: (aliased_import name: (dotted_name) @modul_import))` dan diverifikasi ulang dengan `python q.py t1.py import.scm`. |
| **Tugas 4 & 5** | Menulis query highlight `queries/highlights.scm` untuk mewarnai nama field sebagai `@property` berdasarkan contoh awal di panduan. | Pola contoh awal hanya menyertakan `(comparison field: (identifier) @property)`, sehingga nama field pada node baru `in_expression` (misalnya `status` pada `status in ("open", "pending", "closed")`) tidak ikut terwarnai sebagai `@property`. | Dibuktikan saat menjalankan `tree-sitter query queries/highlights.scm contoh.filter` pada ekspresi `in`. Diperbaiki dengan menambahkan `(in_expression field: (identifier) @property)` sehingga seluruh 18 token pada `contoh.filter` tertangkap dan lulus `tree-sitter highlight --check`. |
| **Tugas 6** | Menguji query JavaScript dan menjalankan `cek.py` melalui perintah terminal one-liner di PowerShell. | AI sempat mengirim string one-liner ke PowerShell yang memuat karakter backtick template literal (`` `...${req.params.id}` ``), sehingga PowerShell menafsirkannya sebagai escape character dan gagal dengan error `The term 'log' is not recognized`. | Dibuktikan dari pesan error terminal PowerShell (`CommandNotFoundException`). Diperbaiki dengan menghindari raw backtick pada argumen PowerShell dan memverifikasi hasil `cek.py` secara manual pada 2 file acak (`api.py` baris 24–71 dan `adapters.py` baris 85–119 & 715) di repositori `psf/requests`. |
