import flet as ft
import subprocess
import threading
import os
import pyperclip
import re
import sys
import atexit


class CrocApp:
    def __init__(self):
        self.output_text = []
        self.current_process = None
        self.process_running = False
        self.output_control = None
        self.page = None
        self.selected_files = []
        self.file_picker = None
        self.file_list = None
        self.croc_code = None
        self.add_files_button = None
        self.send_button = None
        self.code_text = None
        self.output_expander = None
        self.terminate_button = None
        atexit.register(self.cleanup)  # Register cleanup function

    def cleanup(self):
        """Ensure croc process is terminated when app closes"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except:
                if self.current_process:
                    self.current_process.kill()

    def run_croc_command(self, command):
        try:
            self.process_running = True
            self.toggle_buttons(False)  # Disable buttons when process starts
            print(f"Starting command: {command}")

            self.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
            )

            for line in iter(self.current_process.stdout.readline, ""):
                print(f"Raw output: {line}")
                if line.strip():
                    self.output_text.append(line.strip())
                    # Check for croc code in output
                    if "Code is:" in line:
                        code_match = re.search(r"Code is: (.+)", line)
                        if code_match:
                            self.croc_code = code_match.group(1)
                            self.update_code_display()
                    if self.page:
                        self.page.update()
                        self.update_output()

            self.current_process.wait()
            self.output_text.append("Command completed.")
            if self.page:
                self.page.update()
                self.update_output()

        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)
            self.output_text.append(error_message)
            if self.page:
                self.page.update()
                self.update_output()
        finally:
            self.process_running = False
            self.toggle_buttons(True)  # Enable buttons when process ends
            self.current_process = None

    def toggle_buttons(self, enabled):
        if self.add_files_button and self.send_button:
            self.add_files_button.disabled = not enabled
            self.send_button.disabled = not enabled
            self.terminate_button.disabled = (
                enabled  # Enable terminate only when process is running
            )
            self.page.update()

    def update_code_display(self):
        if self.code_text and self.croc_code:
            self.code_text.value = f"Code: {self.croc_code}"
            self.code_text.update()

    def start_croc_command(self, e):
        if not self.process_running:
            if not self.selected_files:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Please select files to send."))
                )
                return

            self.output_text = ["Starting new command..."]
            self.update_output()

            file_paths = " ".join(f'"{file}"' for file in self.selected_files)
            command = f"croc send {file_paths}"

            threading.Thread(
                target=self.run_croc_command, args=(command,), daemon=True
            ).start()
        else:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(
                        "A command is already running. Please wait for it to finish."
                    )
                )
            )

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.update_background()
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.update_background()
        self.page.update()

    def update_background(self):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.bgcolor = ft.colors.TEAL_50
        else:
            self.page.bgcolor = None
        self.page.update()

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            for file in e.files:
                self.selected_files.append(file.path)
            self.update_file_list()

    def update_file_list(self):
        self.file_list.controls.clear()
        for file in self.selected_files:
            self.file_list.controls.append(
                ft.Row(
                    [
                        ft.Text(os.path.basename(file), size=12, expand=True),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            on_click=lambda _, file=file: self.remove_file(file),
                            tooltip="Remove file",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        self.page.update()

    def remove_file(self, file):
        self.selected_files.remove(file)
        self.update_file_list()

    def update_output(self):
        self.output_control.controls = [
            ft.Text(line, size=12) for line in self.output_text[-100:]
        ]
        self.output_control.update()

    def copy_code_to_clipboard(self, e):
        if self.croc_code:
            # Format code based on OS
            if sys.platform == "win32":
                clipboard_text = f"croc {self.croc_code}"
            else:  # Linux and MacOS
                clipboard_text = f'CROC_SECRET="{self.croc_code}" croc'

            pyperclip.copy(clipboard_text)
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Code copied to clipboard!"))
            )
        else:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("No code available to copy."))
            )

    def terminate_process(self, e):
        if self.current_process:
            try:
                # First try to terminate gracefully
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except:
                # If termination fails, force kill
                if self.current_process:
                    self.current_process.kill()

            self.output_text.append("Process terminated.")
            self.update_output()
            self.process_running = False
            self.toggle_buttons(True)
            self.current_process = None

            # Additional cleanup for croc processes
            if sys.platform == "win32":
                os.system("taskkill /F /IM croc.exe 2>NUL")
            else:
                os.system("pkill -9 croc 2>/dev/null")

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Croc Send"
        page.theme_mode = ft.ThemeMode.DARK  # Set dark mode as default
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.TEAL,
            )
        )

        # File Picker
        self.file_picker = ft.FilePicker(on_result=self.pick_files_result)
        page.overlay.append(self.file_picker)

        # Title Row
        title_row = ft.Row(
            [
                ft.Text("Croc Send", size=24, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.icons.LIGHT_MODE,
                    on_click=self.toggle_theme,
                    tooltip="Toggle theme",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Files Label
        files_label = ft.Text("Selected Files:", size=16, weight=ft.FontWeight.BOLD)

        self.add_files_button = ft.ElevatedButton(
            "Add files",
            icon=ft.icons.ADD_ROUNDED,
            on_click=lambda _: self.file_picker.pick_files(allow_multiple=True),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        self.file_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=150,
            width=440,
        )

        file_list_container = ft.Container(
            content=self.file_list,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
            padding=10,
            border_radius=8,
            width=440,
        )

        self.send_button = ft.ElevatedButton(
            "Send",
            icon=ft.icons.SEND_ROUNDED,
            on_click=self.start_croc_command,
            style=ft.ButtonStyle(
                color=ft.colors.ON_PRIMARY,
                bgcolor={ft.MaterialState.DEFAULT: ft.colors.TEAL},
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        # Code Display Section
        self.code_text = ft.Text("Code: ", size=16, weight=ft.FontWeight.BOLD)
        copy_button = ft.IconButton(
            icon=ft.icons.COPY,
            on_click=self.copy_code_to_clipboard,
            tooltip="Copy code",
        )

        code_container = ft.Row(
            [self.code_text, copy_button], alignment=ft.MainAxisAlignment.START
        )

        # Terminate Button
        self.terminate_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_color=ft.colors.RED,
            on_click=self.terminate_process,
            tooltip="Terminate process",
            disabled=True,
        )

        # Output Section with Expander
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

        self.output_expander = ft.ExpansionTile(
            title=ft.Text("Output"),
            controls=[output_container],
            initially_expanded=False,
        )

        # Main Layout
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        title_row,
                        files_label,
                        self.add_files_button,
                        file_list_container,
                        self.send_button,
                        code_container,
                        ft.Row(
                            [ft.Text(""), self.terminate_button],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                        self.output_expander,
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=20,
            )
        )

        self.update_background()


def main():
    app = CrocApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
