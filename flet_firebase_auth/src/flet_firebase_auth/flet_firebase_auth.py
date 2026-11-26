
import flet as ft


@ft.control("FirebaseAuth")
class FirebaseAuth(ft.Service):
    """Firebase service for VibeGram."""

    async def sign_in(self):
        return await self._invoke_method("sign_in", {})

    async def sign_out(self):
        return await self._invoke_method("sign_out", {})

    async def get_auth_state(self):
        return await self._invoke_method("get_auth_state", {})

    async def get_user_profile(self):
        return await self._invoke_method("get_user_profile", {})

    async def save_user_profile(self, profile):
        return await self._invoke_method(
            "save_user_profile",
            {"profile": profile},
        )

    async def search_users(self, query):
        return await self._invoke_method(
            "search_users",
            {"query": query},
        )

    async def create_chat(self, other_uid):
        return await self._invoke_method(
            "create_chat",
            {"otherUid": other_uid},
        )

    async def get_chats(self):
        return await self._invoke_method("get_chats", {})

    async def send_message(self, chat_id, text):
        return await self._invoke_method(
            "send_message",
            {"chatId": chat_id, "text": text},
        )

    async def get_messages(self, chat_id):
        return await self._invoke_method(
            "get_messages",
            {"chatId": chat_id},
        )

    async def create_group(
        self,
        name,
        description="",
        member_uids=None,
    ):
        return await self._invoke_method(
            "create_group",
            {
                "name": name,
                "description": description,
                "memberUids": member_uids or [],
            },
        )

    async def get_groups(self):
        return await self._invoke_method("get_groups", {})

    async def create_channel(
        self,
        name,
        username="",
        description="",
        visibility="Публичный",
    ):
        return await self._invoke_method(
            "create_channel",
            {
                "name": name,
                "username": username,
                "description": description,
                "visibility": visibility,
            },
        )

    async def get_channels(self):
        return await self._invoke_method("get_channels", {})

    async def create_channel_post(self, channel_id, text):
        return await self._invoke_method(
            "create_channel_post",
            {
                "channelId": channel_id,
                "text": text,
            },
        )

    async def get_channel_posts(self, channel_id):
        return await self._invoke_method(
            "get_channel_posts",
            {"channelId": channel_id},
        )

    async def get_settings(self):
        return await self._invoke_method("get_settings", {})

    async def save_settings(self, settings):
        return await self._invoke_method(
            "save_settings",
            {"settings": settings},
        )

    async def get_folders(self):
        return await self._invoke_method("get_folders", {})

    async def create_folder(self, name):
        return await self._invoke_method(
            "create_folder",
            {"name": name},
        )


@ft.control("FletFirebaseAuth")
class FletFirebaseAuth(ft.LayoutControl):
    """VibeGram Firebase control."""

    value: str = ""
