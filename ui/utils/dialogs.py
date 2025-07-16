from kivymd.uix.snackbar import Snackbar

def show_snackbar(text: str, duration: float = 2.5, bg_color=None, text_color=None):
    """A generic snackbar display function."""
    snackbar = Snackbar(text=text, duration=duration)
    if bg_color:
        snackbar.md_bg_color = bg_color
    if text_color:
        snackbar.text_color = text_color
    snackbar.open()

def show_error(text: str):
    # Using red for error
    show_snackbar(text=str(text), bg_color=(0.8, 0.2, 0.2, 1), text_color=(1, 1, 1, 1))

def show_success(text: str):
    # Using green for success
    show_snackbar(text=str(text), bg_color=(0.2, 0.8, 0.2, 1), text_color=(1, 1, 1, 1))
