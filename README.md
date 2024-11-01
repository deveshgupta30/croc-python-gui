# Croc GUI

<p  align="center">    <img  src="assets/crocodile.svg"  alt="CrocGUI Logo"  width="200"/>  </p>

![GitHub release (latest by date)](https://img.shields.io/github/v/release/deveshgupta30/croc-python-gui)
![GitHub](https://img.shields.io/github/license/deveshgupta30/croc-python-gui)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)

Croc GUI is a graphical user interface for the [croc](https://github.com/schollz/croc) file transfer tool, designed to make secure file transfers easier and more accessible.

## About Croc

Croc is a tool that allows any two computers to simply and securely transfer files and folders. It was developed by [Zack Scholl](https://schollz.com/tinker/croc6/) and is available as an open-source project on [GitHub](https://github.com/schollz/croc).

## Features

-   🚀 Simple and intuitive interface for file transfers
-   📋 Easy code sharing with clipboard integration
-   🔒 Secure file transfer using Croc's encryption
-   💻 Cross-platform compatibility (Windows, macOS, Linux)
-   🎨 Modern and clean UI design

## Screenshots

<p float="left">
  <img src="https://github.com/user-attachments/assets/17f63874-8d85-4216-90a0-fbc24f87976a" width="300" />
  <img src="https://github.com/user-attachments/assets/a2e50860-d330-48d3-b7b1-fdc5ea2de547" width="300" />
</p>

## Requirements

-   Python 3.8 or higher
-   Croc command-line tool installed ([Installation Guide](https://github.com/schollz/croc#install))
    -   The app installs croc if not installed.

## Installation

-   Clone this repository:

```
  git clone https://github.com/yourusername/croc-gui.git
  cd croc-gui
```

-   Create venv  
    `python -m venv venv`
-   Activate venv <br>
    Windows: `.\croc-pui\Scripts\activate`<br>
    Linux/macOS: `source venv/bin/activate` <br>
-   Install the required Python packages:
    `pip install -r requirements.txt`

## Usage

Run the app using
`python main.pyw`

1. **Send Files**:

    - Click the "Send File" button
    - Wait for the code to be generated
    - Share the generated code with the recipient
    - The transfer will begin automatically when the recipient enters the code

2. **Receive Files**:
    - Click the "Receive File" button
    - Enter the code provided by the sender
    - Choose your download location
    - Wait for the transfer to complete

## Build Standalone Executable

To build a stand alone executable for your operating system, run the following command:
`python build.py`

## Upcoming Plans

~~1. Integrate receive functionality directly into the GUI.~~ Implemented<br>
~~2. Implement automatic installation of croc if it's not available on the system.~~ Implemented<br> 3. Progress bar<br> 4. Drag and drop<br> 5. Settings page<br> 6. Custom relay options<br> 7. System notifications<br> 8. Bandwidth Limitation<br> 9. Send folders<br>

## Dependencies

-   **Flet**: Modern Flutter-like UI framework for Python
-   **PyInstaller**: Creates standalone executables
-   **Pyperclip**: Handles clipboard operations
-   **Humanize**: Converts bytes to human-readable formats
-   **Croc**: Core file transfer functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   [Zack Scholl](https://schollz.com/) for creating the amazing [croc](https://github.com/schollz/croc) tool.
-   [Flet](https://flet.dev/) for the Python GUI framework used in this project.
-   Icons8: for providing the application icons and graphics
-   **Python Community**: For the excellent libraries and tools
-   **Contributors**: Everyone who has contributed to making CrocGUI better

## Disclaimer

This is an unofficial GUI for croc and is not affiliated with or endorsed by the original croc project or its creators.
