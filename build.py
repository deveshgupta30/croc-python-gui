import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.pyw',
    '--onefile',
    '--windowed',
	'--noconfirm',
	'-n CrocUI',
	'--icon=/assets/crocodile.ico'
])