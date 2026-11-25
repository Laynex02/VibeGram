
import flet as ft


@ft.control("FirebaseAuth")
class FirebaseAuth(ft.Service):
    """VibeGram Firebase authentication service."""

    async def sign_in(self):
        return await self.invoke_method("sign_in")

    async def sign_out(self):
        return await self.invoke_method("sign_out")


@ft.control("FletFirebaseAuth")
class FletFirebaseAuth(ft.LayoutControl):
    """VibeGram Firebase control."""

    value: str = ""
