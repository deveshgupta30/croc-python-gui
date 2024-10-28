from nicegui import ui
import subprocess
import threading
import asyncio

# Global variables to store output
output_container = None
output_text = []
new_output = False
current_process = None
process_running = False  # New flag to track process state


def run_croc_command(command):
    global new_output, current_process, process_running, output_text
    try:
        process_running = True
        current_process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        while True:
            output = current_process.stdout.readline()
            if output == "" and current_process.poll() is not None:
                break
            if output:
                output_text.append(output.strip())
                new_output = True

        rc = current_process.poll()
        output_text.append("Command completed.")
        new_output = True
    except Exception as e:
        output_text.append(f"Error: {str(e)}")
        new_output = True
    finally:
        process_running = False
        current_process = None


def update_output():
    global new_output
    if new_output and output_container:
        output_container.clear()
        with output_container:
            for line in output_text:
                ui.label(line).classes("text-xs")
        new_output = False


def start_croc_command():
    global output_text, new_output, process_running
    if not process_running:
        # Clear previous output
        output_text = ["Starting new command..."]
        new_output = True
        command = 'croc send "C:\\Users\\kesha\\Desktop\\Dev\\croc\\python\\croc-ui.py"'
        threading.Thread(target=run_croc_command, args=(command,), daemon=True).start()
    else:
        ui.notify("A command is already running. Please wait for it to finish.")


@ui.page("/")
def home():
    global output_container

    ui.button("Start Croc Send", on_click=start_croc_command).classes(
        "bg-blue-500 text-white p-2 rounded"
    )
    ui.label("Command Output:").classes("font-bold mt-4")

    # Create a container for output
    output_container = ui.column().classes(
        "w-full p-2 bg-gray-100 rounded min-h-[100px]"
    )

    # Add initial message
    with output_container:
        ui.label("Waiting for command to start...").classes("text-xs")

    # Set up a timer to periodically update the output
    ui.timer(0.1, update_output)


ui.run()
