from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

_dialog = None

def _get_dialog():
    global _dialog
    if not _dialog:
        _dialog = MDDialog(
            buttons=[MDFlatButton(text="OK", on_release=lambda x: _dialog.dismiss())],
        )
    return _dialog

def show_dialog(title, text):
    """A generic dialog display function."""
    dialog = _get_dialog()
    dialog.title = title
    dialog.text = text
    dialog.open()

def show_error(text: str):
    show_dialog(title="Error", text=str(text))

def show_success(text: str):
    show_dialog(title="Success", text=str(text))
