# from nicegui import ui
# import subprocess


# def run_terminal_command(command):
#     try:
#         output = subprocess.check_output(command, shell=True)
#         return output.decode("utf-8").strip()
#     except subprocess.CalledProcessError as e:
#         return f"Error: {e}"


# # Get the Python version before creating the UI
# python_version = run_terminal_command(
#     'croc send "C:\\Users\\kesha\\Desktop\\Dev\\croc\\python\\croc-ui.py"'
# )

# # Create the UI elements
# ui.label(f"Python Version: {python_version}")

# ui.run()

# from nicegui import ui
# import subprocess


# def run_terminal_command(command):
#     try:
#         output = subprocess.check_output(command, shell=True)
#         result = output.decode("utf-8").strip()
#         print(f"Command output: {result}")  # Console debug print
#         return result
#     except subprocess.CalledProcessError as e:
#         print(f"Error occurred: {e}")  # Console debug print
#         return f"Error: {e}"


# # Create multiple UI elements to help debug
# ui.label("Debug Label 1: Starting...")
# python_version = run_terminal_command("git")
# ui.label("Debug Label 2: Command executed")
# ui.label(f"Python Version: {python_version}")
# ui.label("Debug Label 3: Display complete")

# # Add a button to verify UI is responsive
# ui.button("Click me", on_click=lambda: ui.notify("Button clicked!"))

# ui.run(reload=False)

from nicegui import ui
import subprocess
import threading
import asyncio

# Global variables to store output
output_container = None
output_text = []
new_output = False


def run_croc_command(command):
    global new_output
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                output_text.append(output.strip())
                new_output = True

        rc = process.poll()
        return rc
    except Exception as e:
        output_text.append(f"Error: {str(e)}")
        new_output = True


def update_output():
    global new_output
    if new_output and output_container:
        output_container.clear()
        for line in output_text:
            ui.label(line).classes("text-xs")
        new_output = False


def start_croc_command():
    command = 'croc send "C:\\Users\\kesha\\Desktop\\Dev\\croc\\python\\croc-ui.py"'
    threading.Thread(target=run_croc_command, args=(command,), daemon=True).start()


@ui.page("/")
def home():
    global output_container

    ui.button("Start Croc Send", on_click=start_croc_command)
    ui.label("Command Output:")

    # Create a container for output
    output_container = ui.column().classes("w-full p-2 bg-gray-100 rounded")

    # Add initial message
    with output_container:
        ui.label("Waiting for command to start...").classes("text-xs")

    # Set up a timer to periodically update the output
    ui.timer(0.1, update_output)


ui.run()
