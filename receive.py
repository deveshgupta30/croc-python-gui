import os
import subprocess
import sys
import threading
import flet as ft
import asyncio


class ReceiveApp:
    def __init__(self, page):
        self.page = page
        self.code_input = None
        self.output_control = None
        self.directory_label = None
        self.selected_directory = self.get_default_directory()
        self.output_text = []
        self.file_picker = None
        self.current_process = None
        self.process_running = False
        self.terminate_button = None

    def terminate_process(self, e):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except:
                if self.current_process:
                    self.current_process.kill()

            self.output_text.append("Process terminated.")
            self.update_output()
            self.process_running = False
            self.toggle_buttons(True)
            self.current_process = None

            if sys.platform == "win32":
                os.system("taskkill /F /IM croc.exe 2>NUL")
            else:
                os.system("pkill -9 croc 2>/dev/null")

    def toggle_buttons(self, enabled):
        if self.receive_button:
            self.receive_button.disabled = not enabled
            self.terminate_button.disabled = enabled
            self.terminate_button.visible = not enabled
            self.page.update()

    def get_default_directory(self):
        if os.name == "nt":  # Windows
            return os.path.expandvars(r"%USERPROFILE%\Desktop")
        else:  # Linux
            return os.path.expanduser("~")

    def initialize_file_picker(self):
        if self.file_picker is None:
            self.file_picker = ft.FilePicker(on_result=self.directory_picker_result)
            self.page.overlay.append(self.file_picker)
            self.page.update()

    def select_directory(self, e):
        """Open a directory picker and set the selected directory."""
        self.initialize_file_picker()
        self.file_picker.get_directory_path()

    def directory_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle the result of the directory picker."""
        if e.path:
            self.selected_directory = e.path
            self.update_directory_label()

    def update_directory_label(self):
        """Update the directory label with the selected directory."""
        self.directory_label.value = f"Selected directory:\n{self.selected_directory}"
        self.page.update()

    def run_receive_command(self, e):
        """Run the receive command with the provided code."""
        code = self.code_input.value
        if not code:
            self.output_text.append("Error: Please enter a receive code.")
            self.update_output()
            return

        def run_command():
            try:
                self.process_running = True
                self.toggle_buttons(False)
                command = ""
                if os.name == "nt":  # Windows
                    command = f'croc --yes --out "{self.selected_directory}" {code}'
                else:  # Linux
                    command = f"croc --yes --out {self.selected_directory} {code}"

                print(f"Starting command: {command}")

                self.current_process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    universal_newlines=True,
                )

                full_output = ""
                for line in iter(self.current_process.stdout.readline, ""):
                    print(f"Raw output: {line}")
                    full_output += line
                    if line.strip():
                        self.output_text.append(line.strip())
                        if self.page:
                            self.page.update()

                self.current_process.wait()
                self.output_text.append("Command completed.")

                # Check different scenarios
                if "cannot connect" in full_output.lower():
                    self.show_error_dialog(
                        "Connection failed. Please check the code and try again."
                    )
                elif "timed out" in full_output.lower():
                    self.show_error_dialog("Connection timed out. Please try again.")
                elif "100% |" in full_output:
                    self.show_success_dialog()
                else:
                    self.show_failure_dialog(full_output)

                self.page.update()

            except Exception as e:
                error_message = f"Error: {str(e)}"
                print(error_message)
                self.output_text.append(error_message)
                if self.page:
                    self.page.update()
            finally:
                self.process_running = False
                self.toggle_buttons(True)
                self.current_process = None

        # Run the command in a separate thread
        threading.Thread(target=run_command, daemon=True).start()

    def show_error_dialog(self, message):
        """Show an error dialog with a custom message."""
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.close_dialog(error_dialog))
            ],
        )
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()

    def update_output(self):
        """Update the output control with the latest output."""
        self.output_control.controls = [
            ft.Text(line, size=12) for line in self.output_text[-100:]
        ]
        self.output_control.update()

    def show_success_dialog(self):
        """Show a dialog indicating success."""
        success_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Success"),
            content=ft.Text("Files have been received successfully!"),
            actions=[
                ft.TextButton(
                    "OK", on_click=lambda _: self.close_dialog(success_dialog)
                )
            ],
        )
        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()

    def show_failure_dialog(self, output):
        """Show a dialog indicating failure."""
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Transaction Failed"),
            content=ft.Text(
                f"Failed to receive files because the code is not valid.\nLog:\n{output}"
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.close_dialog(error_dialog))
            ],
        )
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()

    def close_dialog(self, dialog):
        """Close the dialog."""
        dialog.open = False
        self.page.update()

    def create_receive_layout(self):
        """Create the receive layout."""
        self.code_input = ft.TextField(
            label="Enter receive code", prefix_icon=ft.icons.CODE, expand=True
        )

        self.directory_label = ft.Text(
            f"Selected directory:\n{self.selected_directory}",
            size=14,
            color=ft.colors.ON_SURFACE_VARIANT,
        )

        select_directory_button = ft.ElevatedButton(
            "Select Directory",
            icon=ft.icons.FOLDER_OPEN,
            on_click=self.select_directory,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self.receive_button = ft.ElevatedButton(
            "Receive Files",
            icon=ft.icons.DOWNLOAD_ROUNDED,
            on_click=self.run_receive_command,
            style=ft.ButtonStyle(
                color=ft.colors.ON_PRIMARY,
                bgcolor={ft.ControlState.DEFAULT: ft.colors.TEAL},
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self.terminate_button = ft.IconButton(
            icon=ft.icons.CANCEL_ROUNDED,
            icon_color=ft.colors.RED_400,
            on_click=self.terminate_process,
            tooltip="Terminate process",
            disabled=True,
            visible=False,
        )

        self.output_control = ft.Column(
            scroll=ft.ScrollMode.AUTO, height=300, spacing=2
        )

        output_container = ft.Container(
            content=self.output_control,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
            padding=10,
            border_radius=8,
            width=440,
        )

        note_text = ft.Text(
            "Note: All files are received by default without any prompt.",
            size=12,
            italic=True,
            color=ft.colors.ON_SURFACE_VARIANT,
        )

        return ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Receive Files", size=24, weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(height=10),
                            self.code_input,
                            ft.Container(height=10),
                            ft.Row(
                                [
                                    select_directory_button,
                                    ft.Container(width=10),
                                    ft.Column([self.directory_label], expand=True),
                                ]
                            ),
                            ft.Container(height=10),
                            note_text,
                            ft.Container(height=10),
                            ft.Row(
                                [self.receive_button, self.terminate_button],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                    ),
                    padding=20,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                    border_radius=12,
                ),
                ft.Container(height=20),
                ft.ExpansionTile(
                    title=ft.Text("Output", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text("Click to expand", italic=True),
                    controls=[output_container],
                    initially_expanded=False,
                ),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )
