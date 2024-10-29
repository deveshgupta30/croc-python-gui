# Croc GUI

Croc GUI is a graphical user interface for the [croc](https://github.com/schollz/croc) file transfer tool, designed to make secure file transfers easier and more accessible.

## About Croc

Croc is a tool that allows any two computers to simply and securely transfer files and folders. It was developed by [Zack Scholl](https://schollz.com/tinker/croc6/) and is available as an open-source project on [GitHub](https://github.com/schollz/croc).

## Features

- User-friendly interface for sending files using croc
- Real-time output display
- Easy code copying for receiving files
- Dark and light theme toggle
- Terminate active transfers

## Requirements

- Python 3.7+
- croc installed and available in system PATH

## Installation

1. Clone this repository:
  ```
  git clone https://github.com/yourusername/croc-gui.git
  cd croc-gui
  ```
2. Install the required Python packages:
   ```pip install -r requirements.txt```


## Usage

Run the application:

1. Click "Add files" to select the files you want to send.
2. Click "Send" to start the transfer.
3. Once the transfer starts, a code will be displayed. Share this code with the receiver.
4. The receiver can use this code with the croc command-line tool to receive the files.

## Upcoming Plans

1. Integrate receive functionality directly into the GUI.
2. Implement automatic installation of croc if it's not available on the system.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Zack Scholl](https://schollz.com/) for creating the amazing [croc](https://github.com/schollz/croc) tool.
- [Flet](https://flet.dev/) for the Python GUI framework used in this project.

## Disclaimer

This is an unofficial GUI for croc and is not affiliated with or endorsed by the original croc project or its creators.
