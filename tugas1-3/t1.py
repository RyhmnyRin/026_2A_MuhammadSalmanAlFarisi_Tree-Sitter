import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

potongan_kode = [
    ("Dasar (assignment)", b"x = 1\n"),
    ("Potongan 1: Fungsi", b"def sapa(nama):\n    return nama\n"),
    ("Potongan 2: if/else", b"if x > 0:\n    y = 1\nelse:\n    y = 2\n"),
    ("Potongan 3: Kelas dengan 1 method", b'class Kucing:\n    def suara(self):\n        return "meong"\n'),
]

for judul, kode in potongan_kode:
    print(f"=== {judul} ===")
    print(kode.decode().rstrip())
    tree = parser.parse(kode)
    print("Pohon S-expression:")
    print(tree.root_node)
    print()

# Inspeksi node bernama vs node anonim pada Potongan 1 (Fungsi)
print("=== Inspeksi Node Bernama vs Anonim (Potongan 1: Fungsi) ===")
tree_fungsi = parser.parse(potongan_kode[1][1])
func_node = tree_fungsi.root_node.children[0]
print("Child langsung dari function_definition (children):")
for c in func_node.children:
    print(f"  {c.type!r:20} -> {'bernama' if c.is_named else 'anonim'}")

print("\nChild di dalam parameters (satu tingkat lebih dalam):")
params_node = func_node.child_by_field_name("parameters")
for c in params_node.children:
    print(f"  {c.type!r:20} -> {'bernama' if c.is_named else 'anonim'}")

print("\nPerbandingan children vs named_children pada function_definition:")
print("  len(children)      :", len(func_node.children), [c.type for c in func_node.children])
print("  len(named_children):", len(func_node.named_children), [c.type for c in func_node.named_children])
print()

# Uji Error Recovery: hapus ':' dan hapus ')'
print("=== Uji Error Recovery ===")
rusak_titik_dua = b"def sapa(nama)\n    return nama\n"
tree_rusak_1 = parser.parse(rusak_titik_dua)
print("1. Hapus ':' setelah def sapa(nama):")
print(tree_rusak_1.root_node)

rusak_kurung = b"def sapa(nama:\n    return nama\n"
tree_rusak_2 = parser.parse(rusak_kurung)
print("\n2. Hapus ')' pada parameter fungsi:")
print(tree_rusak_2.root_node)
