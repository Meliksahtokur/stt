import asyncio
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from src.auth_manager import AuthManager
from src.sync_manager import SyncManager
from src.permissions_manager import PermissionsManager
from ui.utils.dialogs import show_error # Import the centralized dialog utility

# Import screens
from ui.screens.login_screen import LoginScreen
from ui.screens.home_screen import HomeScreen
from ui.screens.animal_details import AnimalDetailsScreen
from ui.screens.add_animal import AddAnimalScreen
from ui.screens.statistics_screen import StatisticsScreen

class WindowManager(ScreenManager):
    pass

class AnimalTrackerApp(MDApp):
    user = ObjectProperty(None, allownone=True)
    auth_manager = ObjectProperty(None)
    sync_manager = ObjectProperty(None)
    permissions_manager = ObjectProperty(None)

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"

        # Initialize AuthManager with callbacks for success/error
        self.auth_manager = AuthManager(
            on_success=self.post_login_setup,
            on_error=show_error # Use centralized dialog utility
        )

        # Load KV files for all screens
        Builder.load_file('ui/screens/home_screen.kv')
        Builder.load_file('ui/screens/animal_details.kv')
        Builder.load_file('ui/screens/add_animal.kv')
        Builder.load_file('ui/screens/statistics_screen.kv')
        Builder.load_file('ui/screens/login_screen.kv') # Load the new login screen KV

        sm = WindowManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AnimalDetailsScreen(name='animal_details'))
        sm.add_widget(AddAnimalScreen(name='add_animal'))
        sm.add_widget(StatisticsScreen(name='statistics'))

        return sm

    def on_start(self):
        # Check for an existing session on app start
        asyncio.create_task(self.auth_manager.check_session())

    def post_login_setup(self, user):
        """Called after a successful login or session recovery."""
        self.user = user
        if self.user:
            # Initialize other managers with the user's ID
            # Pass the supabase client from auth_manager to permissions_manager
            self.sync_manager = SyncManager(user_id=self.user.id)
            self.permissions_manager = PermissionsManager(
                supabase_client=self.auth_manager.supabase, # Use the existing supabase client
                user_id=self.user.id
            )
            self.root.current = 'home'
            # Trigger data load on home screen after login, ensuring it's fully built
            if self.root.get_screen('home'):
                self.root.get_screen('home').load_animal_data()
        else: # This happens on sign_out or if no session
            self.sync_manager = None
            self.permissions_manager = None
            self.root.current = 'login'

if __name__ == '__main__':
    AnimalTrackerApp().run()
