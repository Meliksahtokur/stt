import asyncio
from kivymd.uix.screen import MDScreen
from src.auth_manager import AuthManagerError
from kivymd.app import MDApp
from ui.utils.dialogs import show_error # Assuming dialogs utility from next step

class LoginScreen(MDScreen):

    def sign_in(self):
        email = self.ids.email.text
        password = self.ids.password.text
        if not email or not password:
            show_error("Email and password fields are required.")
            return
        # Use app's auth_manager to handle the async call
        app = MDApp.get_running_app()
        asyncio.create_task(app.auth_manager.sign_in(email, password))

    def sign_up(self):
        # This can be expanded to a separate sign-up screen
        email = self.ids.email.text
        password = self.ids.password.text
        if not email or not password:
            show_error("Email and password fields are required for sign-up.")
            return
        app = MDApp.get_running_app()
        asyncio.create_task(app.auth_manager.sign_up(email, password))
