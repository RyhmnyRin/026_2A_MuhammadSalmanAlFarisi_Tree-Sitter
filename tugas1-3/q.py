import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

kode = open(sys.argv[1], "rb").read()
pola = open(sys.argv[2], encoding="utf-8").read()
tree = parser.parse(kode)

query = Query(PY, pola)
cursor = QueryCursor(query)

if "@params" in pola:
    for _, cap in cursor.matches(tree.root_node):
        nama_nodes = cap.get("nama", [])
        param_nodes = cap.get("params", [])
        if nama_nodes and param_nodes:
            nama = nama_nodes[0].text.decode(errors="replace")
            jumlah = param_nodes[0].named_child_count
            baris = nama_nodes[0].start_point[0] + 1
            print(f"{nama} (baris {baris}): {jumlah} parameter")
else:
    hasil = cursor.captures(tree.root_node)
    for nama, nodes in hasil.items():
        for n in sorted(nodes, key=lambda x: x.start_byte):
            print(f"@{nama}  baris {n.start_point[0] + 1}: {n.text.decode(errors='replace')}")
