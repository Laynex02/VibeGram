
"""Python interface for VibeGram Firebase authentication."""

import flet as ft


@ft.control("FirebaseAuth")
class FirebaseAuth(ft.Service):
    """Native Firebase authentication service."""

    on_result: ft.EventHandler[ft.ControlEvent] | None = None
