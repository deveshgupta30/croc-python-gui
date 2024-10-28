from nicegui import ui
import subprocess
import asyncio
import os

output_container = None
output_text = []
new_output = False
current_process = None
process_running = False
selected_files = []


async def run_croc_command(command):
    global new_output, current_process, process_running, output_text
    try:
        process_running = True
        current_process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await current_process.stdout.readline()
            if line:
                output = line.decode().strip()
                output_text.append(output)
                new_output = True
            else:
                break

        await current_process.wait()
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


async def start_croc_command():
    global output_text, new_output, process_running, selected_files
    if not process_running:
        if not selected_files:
            ui.notify("Please select at least one file before starting the command.")
            return
        output_text = ["Starting new command..."]
        new_output = True
        file_paths = " ".join(f'"{f}"' for f in selected_files)
        command = f"croc send {file_paths}"
        asyncio.create_task(run_croc_command(command))
    else:
        ui.notify("A command is already running. Please wait for it to finish.")


def handle_files(e):
    global selected_files
    for file in e.files:
        file_path = file.name  # This will only give the file name, not the full path
        if file_path not in selected_files:
            selected_files.append(file_path)
    update_file_list()


def update_file_list():
    file_list.clear()
    with file_list:
        if not selected_files:
            ui.label("No files selected").classes("text-sm text-gray-500")
        else:
            for file in selected_files:
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(file).classes("text-sm")
                    ui.button(
                        icon="delete", on_click=lambda f=file: remove_file(f)
                    ).classes("text-red-500")


def remove_file(file):
    global selected_files
    selected_files.remove(file)
    update_file_list()


def clear_file_selection():
    global selected_files
    selected_files = []
    update_file_list()


@ui.page("/")
def home():
    global output_container, file_list

    with ui.column().classes("w-full gap-4"):
        ui.upload(on_upload=handle_files, multiple=True).classes(
            "bg-blue-500 text-white p-2 rounded"
        )

        file_list = ui.column().classes("w-full p-4 bg-gray-100 rounded min-h-[100px]")
        with file_list:
            ui.label("No files selected").classes("text-sm text-gray-500")

        with ui.row().classes("gap-2"):
            ui.button("Clear All Files", on_click=clear_file_selection).classes(
                "bg-red-500 text-white p-2 rounded"
            )
            ui.button("Start Croc Send", on_click=start_croc_command).classes(
                "bg-blue-500 text-white p-2 rounded"
            )

        ui.label("Command Output:").classes("font-bold mt-4")
        output_container = ui.column().classes(
            "w-full p-4 bg-gray-100 rounded min-h-[100px]"
        )
        with output_container:
            ui.label("Waiting for command to start...").classes("text-xs")

    ui.timer(0.1, update_output)


ui.run()
