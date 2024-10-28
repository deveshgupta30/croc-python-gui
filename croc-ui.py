import flet as ft
import subprocess
import threading
import os
import pyperclip


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
        self.croc_code = "123456"  # This should be updated with the actual croc code

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
            command = f'croc send --code "{self.croc_code}" {file_paths}'

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
        if e.files:
            self.selected_files.extend([file.path for file in e.files])
            self.update_file_list()

    def update_file_list(self):
        if self.file_list:
            self.file_list.controls = [
                ft.Row(
                    [
                        ft.Text(os.path.basename(current_file), expand=True),
                        ft.IconButton(
                            ft.icons.DELETE,
                            data=current_file,
                            on_click=lambda e: self.remove_file(e.control.data),
                        ),
                    ]
                )
                for current_file in self.selected_files
            ]
            self.file_list.update()

    def remove_file(self, file):
        print(f"Removing file: {file}")
        if file in self.selected_files:
            self.selected_files.remove(file)
            self.update_file_list()

    def copy_code_to_clipboard(self, e):
        if hasattr(self, "croc_code") and self.croc_code:
            pyperclip.copy(self.croc_code)
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Code copied to clipboard!"))
            )

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Croc Send"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 480
        page.window_height = 640
        page.window_resizable = False

        # Title
        title = ft.Text("Send", size=24, weight=ft.FontWeight.BOLD)

        # File Picker
        self.file_picker = ft.FilePicker(on_result=self.pick_files_result)
        page.overlay.append(self.file_picker)

        # Selected Files Section
        files_label = ft.Text("Selected files", size=16, weight=ft.FontWeight.BOLD)

        add_files_button = ft.ElevatedButton(
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

        # Send Button
        send_button = ft.ElevatedButton(
            "Send",
            icon=ft.icons.SEND_ROUNDED,
            on_click=self.start_croc_command,
            style=ft.ButtonStyle(
                color={ft.MaterialState.DEFAULT: ft.colors.WHITE},
                bgcolor={ft.MaterialState.DEFAULT: ft.colors.BLUE},
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            width=440,
        )

        # Croc Code Section
        code_container = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        f"Code: {self.croc_code}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.icons.SHARE_ROUNDED,
                        on_click=self.copy_code_to_clipboard,
                        tooltip="Copy code to clipboard",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.colors.BLUE_50,
            padding=10,
            border_radius=8,
            width=440,
        )

        # Output Section
        output_label = ft.Text("Command output", size=16, weight=ft.FontWeight.BOLD)

        self.output_control = ft.Column(
            [ft.Text("Waiting for command to start...", size=12)],
            scroll=ft.ScrollMode.ALWAYS,
            height=200,
            width=440,
            auto_scroll=True,
        )

        output_container = ft.Container(
            content=self.output_control,
            bgcolor=ft.colors.BLACK12,
            padding=10,
            border_radius=8,
            width=440,
        )

        # Main Layout
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        title,
                        ft.Divider(height=1),
                        files_label,
                        add_files_button,
                        file_list_container,
                        send_button,
                        code_container,
                        output_label,
                        output_container,
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
