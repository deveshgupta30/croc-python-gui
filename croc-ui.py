import flet as ft
import subprocess
import threading
import os
import pyperclip
import re


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
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
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
            pyperclip.copy(self.croc_code)
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Code copied to clipboard!"))
            )
        else:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("No code available to copy."))
            )

    def terminate_process(self, e):
        if self.current_process:
            self.current_process.terminate()
            self.output_text.append("Process terminated.")
            self.update_output()
            self.process_running = False
            self.toggle_buttons(True)
            self.current_process = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Croc Send"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=ft.colors.TEAL))
        page.window_width = 500
        page.window_height = 800
        page.window_resizable = False
        page.scroll = ft.ScrollMode.AUTO

        # Theme Toggle Button
        theme_toggle = ft.IconButton(
            icon=ft.icons.LIGHT_MODE,
            on_click=self.toggle_theme,
            tooltip="Toggle theme",
            animate_rotation=ft.animation.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
        )

        # Title Row with Theme Toggle
        title_row = ft.Row(
            [ft.Text("Send", size=24, weight=ft.FontWeight.BOLD), theme_toggle],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # File Picker
        self.file_picker = ft.FilePicker(on_result=self.pick_files_result)
        page.overlay.append(self.file_picker)

        # Selected Files Section
        files_label = ft.Text("Selected files", size=16, weight=ft.FontWeight.BOLD)

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
            bgcolor=ft.colors.BLACK12,
            padding=10,
            border_radius=8,
            width=440,
        )

        self.send_button = ft.ElevatedButton(
            "Send",
            icon=ft.icons.SEND_ROUNDED,
            on_click=self.start_croc_command,
            style=ft.ButtonStyle(
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
        terminate_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_color=ft.colors.RED,
            on_click=self.terminate_process,
            tooltip="Terminate process",
        )

        # Output Section with Expander
        output_label = ft.Text("Output", size=16, weight=ft.FontWeight.BOLD)

        self.output_control = ft.Column(
            scroll=ft.ScrollMode.AUTO, height=200, spacing=2
        )

        output_container = ft.Container(
            content=self.output_control,
            bgcolor=ft.colors.BLACK12,
            padding=10,
            border_radius=8,
            width=440,
        )

        self.output_expander = ft.ExpansionTile(
            title=ft.Text("Output"),
            controls=[output_container],
            initially_expanded=True,
        )

        # Main Layout
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        title_row,
                        ft.Divider(height=1),
                        files_label,
                        self.add_files_button,
                        file_list_container,
                        self.send_button,
                        code_container,
                        terminate_button,
                        self.output_expander,
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=20,
            )
        )


def main():
    app = CrocApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
