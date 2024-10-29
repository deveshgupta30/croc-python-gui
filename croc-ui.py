import socket
import flet as ft
import subprocess
import threading
import os
import pyperclip
import re
import sys
import atexit
import time
import asyncio


class CrocApp:
    def __init__(self):
        self.receive_text = None
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
        self.copy_button = None
        self.send_button = None
        self.code_text = None
        self.output_expander = None
        self.terminate_button = None
        self.current_view = "send"  # Track current view
        self.send_toggle = None
        self.receive_toggle = None
        self.main_column = None
        self.terminate_button_visible = False
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except:
                if self.current_process:
                    self.current_process.kill()
        self.close_croc_instances()

    def close_croc_instances(self):
        if sys.platform == "win32":
            os.system("taskkill /F /IM croc.exe 2>NUL")
        else:
            os.system("pkill -9 croc 2>/dev/null")

    def check_winget_available(self):
        try:
            subprocess.run(["winget", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_curl_available(self):
        try:
            subprocess.run(["curl", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    async def check_internet_connection(self):
        """Check if there's an internet connection available."""
        try:
            # Create and show loading dialog
            loading_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "Checking Connection", size=20, weight=ft.FontWeight.BOLD
                ),
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.ProgressRing(width=40, height=40),
                                    ft.Container(height=10),
                                    ft.Text(
                                        "Checking internet connection...",
                                        size=16,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=20,
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            self.page.overlay.append(loading_dialog)
            loading_dialog.open = True
            await self.page.update_async()

            # Try to connect to a reliable host
            socket.create_connection(("8.8.8.8", 53), timeout=3)

            # Close loading dialog
            loading_dialog.open = False
            await self.page.update_async()

            return True

        except OSError:
            # Close loading dialog
            loading_dialog.open = False
            await self.page.update_async()

            # Show error dialog
            error_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "No Internet Connection", size=20, weight=ft.FontWeight.BOLD
                ),
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=ft.icons.WIFI_OFF_ROUNDED,
                            color=ft.colors.RED,
                            size=40,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Please check your internet connection and try again.",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: sys.exit()),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.overlay.append(error_dialog)
            error_dialog.open = True
            await self.page.update_async()

            return False

    async def check_croc_installed(self):
        """Check if croc is installed on the system."""
        loading_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Checking Installation", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ProgressRing(width=40, height=40),
                                ft.Container(height=10),
                                ft.Text(
                                    "Checking if Croc is installed...",
                                    size=16,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        self.page.overlay.append(loading_dialog)
        loading_dialog.open = True
        await self.page.update_async()

        try:
            # Run the command asynchronously
            process = await asyncio.create_subprocess_exec(
                "croc",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                # Wait for the process to complete with a timeout
                await asyncio.wait_for(process.communicate(), timeout=5.0)

                loading_dialog.open = False
                await self.page.update_async()

                if process.returncode == 0:
                    return True
                else:
                    await self.install_croc()
                    return False

            except asyncio.TimeoutError:
                # If the process times out, assume croc is not installed
                loading_dialog.open = False
                await self.page.update_async()
                await self.install_croc()
                return False

        except FileNotFoundError:
            loading_dialog.open = False
            await self.page.update_async()
            await self.install_croc()
            return False

        except Exception as e:
            loading_dialog.open = False
            await self.page.update_async()

            error_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "Installation Check Failed", size=20, weight=ft.FontWeight.BOLD
                ),
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=ft.icons.ERROR_OUTLINE, color=ft.colors.RED, size=40
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            f"An error occurred while checking Croc installation:\n{str(e)}",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                actions=[
                    ft.TextButton(
                        "OK", on_click=lambda _: setattr(error_dialog, "open", False)
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.overlay.append(error_dialog)
            error_dialog.open = True
            await self.page.update_async()
            return False

    async def install_croc(self):
        def close_dialog(dialog):
            dialog.open = False
            self.page.update()

        pass

        def handle_installation():
            try:
                if sys.platform == "win32":
                    if not self.check_winget_available():
                        raise Exception("Winget is not available on this system.")
                    subprocess.run(["winget", "install", "schollz.croc"], check=True)
                else:
                    if not self.check_curl_available():
                        raise Exception("Curl is not available on this system.")

                    # Ask for sudo password
                    sudo_password = self.get_sudo_password()
                    if sudo_password is None:
                        raise Exception("Sudo password is required for installation.")

                    command = "curl https://getcroc.schollz.com | sudo -S bash"
                    process = subprocess.Popen(
                        command,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    stdout, stderr = process.communicate(input=f"{sudo_password}\n")

                    if process.returncode != 0:
                        raise Exception(f"Installation failed: {stderr}")

                # Check if installation was successful
                if self.check_croc_installed():
                    success_dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Success"),
                        content=ft.Text("Croc has been successfully installed!"),
                        actions=[
                            ft.TextButton(
                                "OK", on_click=lambda _: close_dialog(success_dialog)
                            ),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.overlay.append(success_dialog)
                    success_dialog.open = True
                    self.page.update()
                else:
                    raise Exception("Installation verification failed")

            except Exception as e:
                error_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Installation Failed"),
                    content=ft.Text(
                        f"Failed to install Croc: {str(e)}\n"
                        "Please install it manually:\n"
                        "Windows: winget install schollz.croc\n"
                        "Linux/MacOS: curl https://getcroc.schollz.com | sudo bash\n"
                        "For more info, go to https://github.com/schollz/croc"
                    ),
                    actions=[
                        ft.TextButton(
                            "OK", on_click=lambda _: close_dialog(error_dialog)
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                self.page.overlay.append(error_dialog)
                error_dialog.open = True
                self.page.update()

        install_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Croc Not Found"),
            content=ft.Text(
                "Croc is not installed on your system. Would you like to install it now?"
            ),
            actions=[
                ft.TextButton(
                    "Yes",
                    on_click=lambda _: (
                        close_dialog(install_dialog),
                        handle_installation(),
                    ),
                ),
                ft.TextButton(
                    "No", on_click=lambda _: (close_dialog(install_dialog), sys.exit())
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(install_dialog)
        install_dialog.open = True
        self.page.update()

    def get_sudo_password(self):
        def close_dialog(dialog):
            dialog.open = False
            self.page.update()

        password_input = ft.TextField(
            label="Sudo Password", password=True, can_reveal_password=True
        )

        def on_submit(_):
            close_dialog(password_dialog)
            self.sudo_password = password_input.value

        password_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Sudo Password Required"),
            content=ft.Column(
                [
                    ft.Text("Please enter your sudo password to install Croc:"),
                    password_input,
                ]
            ),
            actions=[
                ft.TextButton("Submit", on_click=on_submit),
                ft.TextButton(
                    "Cancel", on_click=lambda _: close_dialog(password_dialog)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.sudo_password = None
        self.page.overlay.append(password_dialog)
        password_dialog.open = True
        self.page.update()

        # Wait for the dialog to close
        while password_dialog.open:
            time.sleep(0.1)

        return self.sudo_password

    def switch_view(self, view):
        self.current_view = view
        if view == "send":
            self.send_toggle.style.color = ft.colors.ON_SURFACE
            self.receive_toggle.style.color = ft.colors.ON_SURFACE_VARIANT
            self.main_column.visible = True
            self.receive_text.visible = False
        else:  # receive view
            self.send_toggle.style.color = ft.colors.ON_SURFACE_VARIANT
            self.receive_toggle.style.color = ft.colors.ON_SURFACE
            self.main_column.visible = False
            self.receive_text.visible = True
        self.page.update()

    def run_croc_command(self, command):
        try:
            self.process_running = True
            self.toggle_buttons(False)
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
            self.toggle_buttons(True)
            self.current_process = None

    def toggle_buttons(self, enabled):
        if self.add_files_button and self.send_button:
            self.add_files_button.disabled = not enabled
            self.send_button.disabled = not enabled
            self.terminate_button.disabled = enabled
            self.terminate_button.visible = not enabled
            self.page.update()

    def update_code_display(self):
        if self.code_text and self.croc_code:
            self.code_text.value = f"Code: {self.croc_code}"
            self.code_text.visible = True
            self.copy_button.visible = True
            self.code_text.update()
            self.copy_button.update()

    def start_croc_command(self, e):
        if not self.process_running:
            if not self.selected_files:
                self.page.open(
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
            self.page.open(
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

    def check_croc_running(self):
        if sys.platform == "win32":
            cmd = 'tasklist /FI "IMAGENAME eq croc.exe" /NH'
            output = subprocess.check_output(cmd, shell=True).decode()
            return "croc.exe" in output
        else:
            try:
                cmd = "pgrep croc"
                subprocess.check_output(cmd, shell=True)
                return True
            except subprocess.CalledProcessError:
                return False

    def show_croc_running_dialog(self):
        def close_croc():
            if sys.platform == "win32":
                os.system("taskkill /F /IM croc.exe 2>NUL")
            else:
                os.system("pkill -9 croc 2>/dev/null")
            dialog.open = False
            self.page.update()

        def close_warning_dialog(warning_dialog):
            warning_dialog.open = False
            self.page.update()

        def show_warning():
            dialog.open = False
            self.page.update()
            warning_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Warning"),
                content=ft.Text(
                    "Multiple croc sessions running in background may impact system performance."
                ),
                actions=[
                    ft.TextButton(
                        "OK",
                        on_click=lambda _: close_warning_dialog(warning_dialog),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.overlay.append(warning_dialog)
            warning_dialog.open = True
            # self.page.dialog = warning_dialog
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Croc Process Running"),
            content=ft.Text(
                "A Croc process is already running in the background. "
                "This might interfere with the application. "
                "Would you like to close it?"
            ),
            actions=[
                ft.TextButton("Yes", on_click=lambda _: close_croc()),
                ft.TextButton("No", on_click=lambda _: show_warning()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # self.page.dialog = dialog
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

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
            if sys.platform == "win32":
                clipboard_text = f"croc {self.croc_code}"
            else:
                clipboard_text = f'CROC_SECRET="{self.croc_code}" croc'

            pyperclip.copy(clipboard_text)
            self.page.open(ft.SnackBar(content=ft.Text("Code copied to clipboard!")))
        else:
            self.page.open(ft.SnackBar(content=ft.Text("No code available to copy.")))

    def terminate_process(self, e):
        if self.current_process:
            self.code_text.visible = False
            self.terminate_button.visible = False
            self.copy_button.visible = False
            self.code_text.update()
            self.copy_button.update()
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

    async def main(self, page: ft.Page):
        self.page = page
        page.window.width = 480
        page.window.height = 700
        page.window.resizable = False
        page.window.maximizable = False
        page.scroll = "adaptive"
        page.title = "Croc GUI"
        page.theme_mode = ft.ThemeMode.DARK
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.TEAL,
            )
        )
        page.window.prevent_close = False
        page.window.icon = "./assets/crocodile.svg"
        page.on_close = self.cleanup

        if not await self.check_internet_connection():
            return

        if not await self.check_croc_installed():
            self.install_croc()
        else:
            # Continue with the rest of your initialization
            if self.check_croc_running():
                self.show_croc_running_dialog()

        if self.check_croc_running():
            self.page = page
            self.show_croc_running_dialog()

        # File Picker
        self.file_picker = ft.FilePicker(on_result=self.pick_files_result)
        page.overlay.append(self.file_picker)

        # Title Row with Toggle
        title_row = ft.Row(
            [
                ft.Image(
                    src="./assets/crocodile.svg",
                    width=30,
                    height=30,
                    color=ft.colors.ON_SURFACE,
                ),
                ft.Text("Croc GUI", size=24, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.icons.LIGHT_MODE,
                    on_click=self.toggle_theme,
                    tooltip="Toggle theme",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Toggle Buttons Row
        self.send_toggle = ft.TextButton(
            text="Send",
            style=ft.ButtonStyle(
                color=ft.colors.ON_SURFACE,
            ),
            on_click=lambda _: self.switch_view("send"),
        )

        self.receive_toggle = ft.TextButton(
            text="Receive",
            style=ft.ButtonStyle(
                color=ft.colors.ON_SURFACE_VARIANT,
            ),
            on_click=lambda _: self.switch_view("receive"),
        )

        toggle_row = ft.Row(
            [
                self.send_toggle,
                ft.Text("|", size=16, color=ft.colors.ON_SURFACE_VARIANT),
                self.receive_toggle,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
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
                bgcolor={ft.ControlState.DEFAULT: ft.colors.TEAL},
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        # Code Display Section
        self.code_text = ft.Text(
            "Code: ", size=16, weight=ft.FontWeight.BOLD, visible=False
        )
        self.copy_button = ft.IconButton(
            icon=ft.icons.COPY,
            on_click=self.copy_code_to_clipboard,
            tooltip="Copy code",
            visible=False,
        )

        code_container = ft.Row(
            [self.code_text, self.copy_button],
            alignment=ft.MainAxisAlignment.START,
        )

        # Terminate Button
        self.terminate_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_color=ft.colors.RED,
            on_click=self.terminate_process,
            tooltip="Terminate process",
            disabled=True,
            visible=False,
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

        # Main content column
        self.main_column = ft.Column(
            [
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
        )

        # Receive view text
        self.receive_text = ft.Text(
            "Feature under development",
            size=16,
            color=ft.colors.ON_SURFACE_VARIANT,
            visible=False,
        )

        # Main Layout
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        title_row,
                        toggle_row,
                        self.main_column,
                        self.receive_text,
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
    ft.app(
        target=app.main,
        assets_dir="assets",
        web_renderer="html",
        view=ft.AppView.FLET_APP,
    )


if __name__ == "__main__":
    main()
