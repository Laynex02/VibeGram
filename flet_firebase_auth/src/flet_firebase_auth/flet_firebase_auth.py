
import flet as ft


@ft.control("FirebaseAuth")
class FirebaseAuth(ft.Service):
    """VibeGram Firebase authentication service."""

    async def sign_in(self):
        return await self._invoke_method("sign_in", {})

    async def sign_out(self):
        return await self._invoke_method("sign_out", {})

    async def get_auth_state(self):
        return await self._invoke_method("get_auth_state", {})

    async def get_user_profile(self):
        return await self._invoke_method("get_user_profile", {})

    async def save_user_profile(self, profile):
        return await self._invoke_method("save_user_profile", profile)


@ft.control("FletFirebaseAuth")
class FletFirebaseAuth(ft.LayoutControl):
    """VibeGram Firebase control."""

    value: str = ""
