import flet as ft
import subprocess
import threading
import os


class CrocApp:
    def __init__(self):
        self.output_text = []
        self.current_process = None
        self.process_running = False
        self.output_control = None
        self.page = None
        self.selected_files = []
        self.file_picker = None

    def run_croc_command(self, command):
        try:
            self.process_running = True
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
            self.current_process = None

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

    def update_output(self):
        if self.output_control and self.page:
            self.output_control.controls = [
                ft.Text(line, size=12) for line in self.output_text
            ]
            self.output_control.update()

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        self.selected_files = [file.path for file in e.files] if e.files else []
        print("Selected files:", self.selected_files)

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Croc Send UI"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 800
        page.window_height = 600

        self.file_picker = ft.FilePicker(on_result=self.pick_files_result)
        page.overlay.append(self.file_picker)

        pick_files_button = ft.ElevatedButton(
            "Pick files",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.file_picker.pick_files(allow_multiple=True),
        )

        start_button = ft.ElevatedButton(
            "Start Croc Send",
            on_click=self.start_croc_command,
            style=ft.ButtonStyle(
                color={ft.MaterialState.DEFAULT: ft.colors.WHITE},
                bgcolor={ft.MaterialState.DEFAULT: ft.colors.BLUE},
            ),
        )

        self.output_control = ft.Column(
            [ft.Text("Waiting for command to start...", size=12)],
            scroll=ft.ScrollMode.ALWAYS,
            height=300,
            width=600,
            auto_scroll=True,
        )

        output_container = ft.Container(
            content=self.output_control,
            bgcolor=ft.colors.BLACK12,
            padding=10,
            border_radius=10,
        )

        page.add(
            ft.Column(
                [
                    pick_files_button,
                    start_button,
                    ft.Text("Command Output:", weight=ft.FontWeight.BOLD, size=16),
                    output_container,
                ],
                spacing=20,
            )
        )


def main(page: ft.Page):
    app = CrocApp()
    app.main(page)


ft.app(target=main)
