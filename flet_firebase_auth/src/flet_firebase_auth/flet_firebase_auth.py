
import flet as ft


@ft.control("FirebaseAuth")
class FirebaseAuth(ft.Service):
    """Firebase authentication service."""


@ft.control("FletFirebaseAuth")
class FletFirebaseAuth(ft.LayoutControl):
    """VibeGram Firebase control."""

    value: str = ""
