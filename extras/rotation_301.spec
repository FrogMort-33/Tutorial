# rotation_301.spec - how to build rotation_301.exe (one file, no console window, the lava tank icon).
# Build it from the extras folder with:   py -m PyInstaller rotation_301.spec
# The .exe lands in extras\dist\ (build\ and dist\ are scratch folders: not kept in git).
# PyInstaller finds rotation_data / rotation_functions / rotation_levels itself, from the imports.

a = Analysis(
    ["rotation_301.py"],
    datas=[("rotation_301_icon.png", ".")],   # the window icon, loaded while the game runs
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="rotation_301",
    icon="rotation_301_icon.ico",             # the .exe's own icon (in Explorer)
    console=False,                            # --windowed: no black console window behind the game
)
