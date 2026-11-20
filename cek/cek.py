import sys
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

Q_TODO = Query(PY, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNGSI = Query(PY, "(function_definition name: (identifier) @nama) @fungsi")


def cek_file(path):
    tree = parser.parse(path.read_bytes())

    # Fitur 1: komentar TODO/FIXME (sudah jadi)
    for node in QueryCursor(Q_TODO).captures(tree.root_node).get("c", []):
        print(f"{path}:{node.start_point[0] + 1}: {node.text.decode().strip()}")

    # Fitur 2: fungsi yang lebih dari 30 baris
    for _, cap in QueryCursor(Q_FUNGSI).matches(tree.root_node):
        fungsi_node = cap["fungsi"][0]
        nama_node = cap["nama"][0]
        panjang = fungsi_node.end_point[0] - fungsi_node.start_point[0] + 1
        if panjang > 30:
            nama = nama_node.text.decode(errors="replace")
            baris = fungsi_node.start_point[0] + 1
            print(f"{path}:{baris}: fungsi '{nama}' terlalu panjang ({panjang} baris)")

    # Fitur 3 (TODO): file yang pohonnya mengandung error


for path in Path(sys.argv[1]).rglob("*.py"):
    cek_file(path)
