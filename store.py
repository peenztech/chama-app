from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
)

from kivy.utils import get_color_from_hex
class DialogManager:
    dialog = None

    @classmethod
    def show_dialog(cls, title, message, color="default"):
        """Reusable dialog for KivyMD 2.0.1.dev0."""
        color_map = {
            "success": "#4CAF50",
            "error": "#E53935",
            "info": "#2196F3",
            "default": "#424242",
        }

        bg_color = get_color_from_hex(color_map.get(color, "#424242"))

        # Close existing dialog if open
        if cls.dialog:
            cls.dialog.dismiss()

        # ✅ New-style MDDialog definition
        cls.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogSupportingText(text=message),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    on_release=lambda x: cls.dialog.dismiss(),
                ),
            ),
            md_bg_color=bg_color,
        )

        cls.dialog.open()
