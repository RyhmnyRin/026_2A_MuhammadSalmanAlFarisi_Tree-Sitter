import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

Q_TODO = Query(PY, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNGSI = Query(PY, "(function_definition name: (identifier) @nama) @fungsi")


def cari_error_pertama(node):
    if node.is_error or node.is_missing:
        return node
    for child in node.children:
        if child.has_error or child.is_error or child.is_missing:
            hasil = cari_error_pertama(child)
            if hasil is not None:
                return hasil
    return None


def cek_file(path):
    tree = parser.parse(path.read_bytes())

    # Fitur 1: komentar TODO/FIXME (sudah jadi)
    for node in QueryCursor(Q_TODO).captures(tree.root_node).get("c", []):
        teks = node.text.decode(errors="replace").strip()
        print(f"{path}:{node.start_point[0] + 1}: {teks}")

    # Fitur 2: fungsi yang lebih dari 30 baris
    for _, cap in QueryCursor(Q_FUNGSI).matches(tree.root_node):
        fungsi_node = cap["fungsi"][0]
        nama_node = cap["nama"][0]
        panjang = fungsi_node.end_point[0] - fungsi_node.start_point[0] + 1
        if panjang > 30:
            nama = nama_node.text.decode(errors="replace")
            baris = fungsi_node.start_point[0] + 1
            print(f"{path}:{baris}: fungsi '{nama}' terlalu panjang ({panjang} baris)")

    # Fitur 3: file yang pohonnya mengandung error
    if tree.root_node.has_error:
        err_node = cari_error_pertama(tree.root_node)
        baris = (err_node.start_point[0] + 1) if err_node else 1
        print(f"{path}:{baris}: ditemukan syntax error pada file")


LEWATI = {"venv", ".venv", ".git", "node_modules"}
for path in Path(sys.argv[1]).rglob("*.py"):
    if any(bagian in LEWATI for bagian in path.parts):
        continue
    cek_file(path)
