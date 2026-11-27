
import flet as ft
from flet_firebase_auth import FirebaseAuth


def main(page: ft.Page):
    # ==========================================
    # SERVICES
    # ==========================================
    firebase_auth = FirebaseAuth()
    page.services.append(firebase_auth)

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # ==========================================
    # APP SETTINGS
    # ==========================================
    page.title = "VibeGram"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#090914"
    page.padding = 0
    page.spacing = 0

    C = {
        "bg": "#090914",
        "panel": "#141426",
        "panel2": "#1D1B35",
        "purple": "#8B5CF6",
        "blue": "#3B82F6",
        "cyan": "#22D3EE",
        "text": "#F5F3FF",
        "muted": "#9292AC",
        "border": "#292944",
        "danger": "#F87171",
    }

    state = {
        "authenticated": False,
        "auth_loading": True,
        "auth_mode": "login",
        "uid": "",
        "email": "",
        "tab": "Чаты",
        "subpage": None,
        "selected_channel": None,
        "username": "",
        "display_name": "",
        "about": "",
        "avatar": None,
        "profile_bg": None,
        "groups": [],
        "channels": [],
        "folders": [],
        "notifications": True,
        "message_notifications": True,
        "group_notifications": True,
        "channel_notifications": True,
        "sound": True,
        "vibration": True,
        "show_online": True,
        "show_phone": False,
        "show_photo": True,
        "allow_messages": True,
        "allow_groups": True,
        "read_receipts": True,
        "language": "Русский",
        "font_size": "Средний",
        "chat_wallpaper": "Стандартные",
        "auto_download": True,
        "theme": "dark",
        "vibe_plus": False,
    }

    # ==========================================
    # HELPERS
    # ==========================================
    def txt(value, size=14, color=None, weight=None):
        return ft.Text(
            str(value),
            size=size,
            color=color or C["text"],
            weight=weight,
        )

    def panel(control, padding=16):
        return ft.Container(
            content=control,
            padding=padding,
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            border_radius=18,
        )

    def heading(title, subtitle=None):
        items = [txt(title, 25, weight=ft.FontWeight.BOLD)]

        if subtitle:
            items.append(txt(subtitle, 13, C["muted"]))

        return ft.Column(items, spacing=5)

    def button(label, callback, icon=None):
        return ft.ElevatedButton(
            content=txt(label, 14, "white", ft.FontWeight.BOLD),
            icon=icon,
            on_click=callback,
            bgcolor=C["purple"],
            color="white",
            height=49,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15),
            ),
        )

    def outline_button(label, callback, icon=None):
        return ft.OutlinedButton(
            content=txt(label),
            icon=icon,
            on_click=callback,
            style=ft.ButtonStyle(
                color=C["cyan"],
                side=ft.BorderSide(1, C["border"]),
                shape=ft.RoundedRectangleBorder(radius=14),
            ),
        )

    def field(label, hint="", value=""):
        return ft.TextField(
            label=label,
            hint_text=hint,
            value=value,
            color=C["text"],
            border_color=C["border"],
            focused_border_color=C["purple"],
            bgcolor=C["panel"],
            border_radius=12,
        )

    def notify(message):
        page.snack_bar = ft.SnackBar(content=txt(message))
        page.snack_bar.open = True
        page.update()

    def empty(icon, title, subtitle):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=25,
            content=ft.Column(
                [
                    ft.Icon(icon, size=58, color=C["purple"]),
                    txt(title, 19, weight=ft.FontWeight.BOLD),
                    txt(subtitle, 13, C["muted"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
        )

    def section(icon, title, subtitle, callback):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=C["cyan"], size=24),
                        bgcolor="#25213F",
                        padding=13,
                        border_radius=14,
                    ),
                    ft.Column(
                        [
                            txt(title, 15, weight=ft.FontWeight.BOLD),
                            txt(subtitle, 12, C["muted"]),
                        ],
                        expand=True,
                        spacing=4,
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        color=C["muted"],
                    ),
                ],
                spacing=12,
            ),
            padding=15,
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            border_radius=17,
            on_click=callback,
            ink=True,
        )

    # ==========================================
    # GOOGLE AUTHENTICATION
    # ==========================================
    async def google_sign_in(e):
        try:
            notify("Подключаем Google...")

            result = await firebase_auth.sign_in()

            if not isinstance(result, dict):
                notify("Не удалось получить ответ Firebase")
                return

            if not result.get("success"):
                notify(
                    "Ошибка входа: "
                    + str(result.get("error", "Неизвестная ошибка"))
                )
                return

            state["uid"] = result.get("uid", "")
            state["email"] = result.get("email", "")
            state["display_name"] = (
                result.get("displayName", "")
                or state["display_name"]
            )
            state["authenticated"] = True

            notify("Добро пожаловать в VibeGram!")
            render()

        except Exception as ex:
            notify(f"Ошибка Google: {ex}")

    def start_google_sign_in(e):
        print("VIBEGRAM: GOOGLE BUTTON CLICKED")
        page.run_task(google_sign_in, e)

    async def google_sign_out(e):
        try:
            result = await firebase_auth.sign_out()

            if isinstance(result, dict) and not result.get("success"):
                notify(str(result.get("error", "Ошибка выхода")))
                return

            state["authenticated"] = False
            state["uid"] = ""
            state["email"] = ""
            state["tab"] = "Чаты"
            state["subpage"] = None

            notify("Ты вышел из аккаунта")
            render()

        except Exception as ex:
            notify(f"Ошибка выхода: {ex}")

    # ==========================================
    # RESTORE FIREBASE SESSION
    # ==========================================
    async def restore_auth():
        try:
            result = await firebase_auth.get_auth_state()

            if isinstance(result, dict) and result.get("success"):
                if result.get("authenticated"):
                    state["authenticated"] = True
                    state["uid"] = result.get("uid", "")
                    state["email"] = result.get("email", "")
                    state["display_name"] = (
                        result.get("displayName", "")
                        or state["display_name"]
                    )

        except Exception as ex:
            print(f"VibeGram auth restore error: {ex}")

        state["auth_loading"] = False
        render()

    # ==========================================
    # WELCOME / AUTH SCREEN
    # ==========================================
    def auth_screen():
        is_login = state["auth_mode"] == "login"

        def switch_mode(mode):
            state["auth_mode"] = mode
            render()

        logo = ft.Container(
            content=ft.Stack(
                [
                    ft.Container(
                        width=100,
                        height=100,
                        border_radius=30,
                        gradient=ft.LinearGradient(
                            colors=[C["purple"], C["blue"], C["cyan"]],
                        ),
                    ),
                    ft.Container(
                        content=txt("V", 55, "white", ft.FontWeight.BOLD),
                        width=100,
                        height=100,
                        alignment=ft.Alignment.CENTER,
                    ),
                ]
            ),
            shadow=ft.BoxShadow(
                blur_radius=35,
                color="#558B5CF6",
            ),
        )

        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=25,
            content=ft.Column(
                [
                    logo,
                    txt("VibeGram", 34, weight=ft.FontWeight.BOLD),
                    txt(
                        "Общайся. Создавай. Будь собой.",
                        14,
                        C["muted"],
                    ),
                    ft.Container(height=25),
                    panel(
                        ft.Column(
                            [
                                txt(
                                    "Добро пожаловать!",
                                    22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                txt(
                                    "Войди или создай аккаунт VibeGram.",
                                    13,
                                    C["muted"],
                                ),
                                ft.Container(height=10),
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=txt(
                                                "Войти",
                                                13,
                                                "white" if is_login else C["muted"],
                                            ),
                                            bgcolor=C["purple"] if is_login else None,
                                            padding=12,
                                            border_radius=12,
                                            expand=True,
                                            alignment=ft.Alignment.CENTER,
                                            on_click=lambda e: switch_mode("login"),
                                            ink=True,
                                        ),
                                        ft.Container(
                                            content=txt(
                                                "Регистрация",
                                                13,
                                                "white" if not is_login else C["muted"],
                                            ),
                                            bgcolor=C["purple"] if not is_login else None,
                                            padding=12,
                                            border_radius=12,
                                            expand=True,
                                            alignment=ft.Alignment.CENTER,
                                            on_click=lambda e: switch_mode("register"),
                                            ink=True,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                ft.Container(height=10),
                                button(
                                    "Продолжить с Google",
                                    start_google_sign_in,
                                    ft.Icons.LOGIN,
                                ),
                                txt(
                                    "При первом входе Firebase автоматически "
                                    "создаст аккаунт. При повторном входе "
                                    "откроется существующий аккаунт.",
                                    11,
                                    C["muted"],
                                ),
                            ],
                            spacing=13,
                        )
                    ),
                    ft.Container(height=15),
                    txt("VibeGram • Версия 1.0", 11, C["muted"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    # ==========================================
    # IMAGE PICKER
    # ==========================================
    async def pick_image(callback):
        try:
            files = await file_picker.pick_files(
                dialog_title="Выбери изображение",
                file_type=ft.FilePickerFileType.IMAGE,
                allow_multiple=False,
            )

            if not files:
                return

            if not files[0].path:
                notify("Не удалось получить файл")
                return

            callback(files[0].path)
            render()

        except Exception as ex:
            notify(f"Ошибка изображения: {ex}")

    async def choose_avatar(e):
        await pick_image(
            lambda path: state.update({"avatar": path})
        )

    async def choose_background(e):
        await pick_image(
            lambda path: state.update({"profile_bg": path})
        )

    # ==========================================
    # PROFILE
    # ==========================================
    def edit_profile(e):
        name = field("Имя", "Твоё имя", state["display_name"])
        username = field("Username", "Например, vibe_user", state["username"])
        about = field("О себе", "Расскажи о себе", state["about"])

        def save(ev):
            value = (username.value or "").strip().lstrip("@")

            if not value:
                notify("Введи username")
                return

            state["display_name"] = (name.value or "").strip()
            state["username"] = value
            state["about"] = (about.value or "").strip()

            page.pop_dialog()
            render()
            notify("Профиль обновлён")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=txt("Редактирование профиля", 20),
                content=ft.Column(
                    [name, username, about],
                    tight=True,
                    width=300,
                    spacing=12,
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.TextButton("Сохранить", on_click=save),
                ],
            )
        )

    def profile_screen():
        if state["avatar"]:
            avatar = ft.Container(
                content=ft.Image(
                    src=state["avatar"],
                    width=105,
                    height=105,
                    fit=ft.BoxFit.COVER,
                ),
                width=105,
                height=105,
                border_radius=60,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        else:
            avatar = ft.Container(
                content=ft.Icon(
                    ft.Icons.PERSON,
                    size=55,
                    color=C["cyan"],
                ),
                width=105,
                height=105,
                border_radius=60,
                bgcolor="#25213F",
                alignment=ft.Alignment.CENTER,
            )

        background = (
            ft.Image(
                src=state["profile_bg"],
                width=500,
                height=260,
                fit=ft.BoxFit.COVER,
            )
            if state["profile_bg"]
            else ft.Container(
                gradient=ft.LinearGradient(
                    colors=["#35205E", "#17172E", "#102B40"],
                )
            )
        )

        banner = ft.Container(
            content=ft.Stack(
                [
                    background,
                    ft.Container(
                        content=ft.Column(
                            [
                                avatar,
                                txt(
                                    state["display_name"] or "Твоё имя",
                                    22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                txt(
                                    "@" + state["username"]
                                    if state["username"]
                                    else "@username",
                                    13,
                                    C["muted"],
                                ),
                                txt(
                                    state["about"] or "Расскажи о себе",
                                    12,
                                    C["muted"],
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        alignment=ft.Alignment.CENTER,
                        bgcolor="#99090914",
                        expand=True,
                    ),
                ]
            ),
            height=260,
            border_radius=22,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.Border.all(1, C["border"]),
        )

        return ft.Column(
            [
                heading("Профиль", "Твоя страница VibeGram"),
                banner,
                ft.Row(
                    [
                        ft.Container(
                            content=outline_button(
                                "Аватар",
                                choose_avatar,
                                ft.Icons.CAMERA_ALT_OUTLINED,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=outline_button(
                                "Фон",
                                choose_background,
                                ft.Icons.IMAGE_OUTLINED,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=8,
                ),
                button("Изменить профиль", edit_profile, ft.Icons.EDIT),
                panel(
                    ft.Column(
                        [
                            txt("Аккаунт Google", 15, weight=ft.FontWeight.BOLD),
                            txt(state["email"], 12, C["muted"]),
                            txt("Подключён", 12, "#22C55E"),
                        ],
                        spacing=6,
                    )
                ),
                outline_button(
                    "Выйти из аккаунта",
                    google_sign_out,
                    ft.Icons.LOGOUT,
                ),
                section(
                    ft.Icons.STAR,
                    "Vibe+",
                    "Премиальные возможности",
                    lambda e: open_subpage("plus"),
                ),
                section(
                    ft.Icons.SHIELD_OUTLINED,
                    "Приватность",
                    "Настройки безопасности",
                    lambda e: open_subpage("privacy"),
                ),
                section(
                    ft.Icons.NOTIFICATIONS_OUTLINED,
                    "Уведомления",
                    "Настройки уведомлений",
                    lambda e: open_subpage("notifications"),
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    # ==========================================
    # CHANNEL CREATION
    # ==========================================
    def create_channel(e):
        name = field("Название канала", "Например, VibeGram News")
        username = field("Username канала", "Например, vibegram_news")
        description = field("Описание", "О чём твой канал?")

        visibility = ft.Dropdown(
            label="Тип канала",
            value="Публичный",
            options=[
                ft.dropdown.Option("Публичный"),
                ft.dropdown.Option("Приватный"),
            ],
            border_color=C["border"],
        )

        channel_avatar = {"path": None}

        avatar_preview = ft.Container(
            content=ft.Icon(
                ft.Icons.CAMPAIGN_OUTLINED,
                size=35,
                color=C["cyan"],
            ),
            width=85,
            height=85,
            border_radius=50,
            bgcolor="#25213F",
            alignment=ft.Alignment.CENTER,
        )

        async def choose_channel_avatar(ev):
            try:
                files = await file_picker.pick_files(
                    dialog_title="Аватар канала",
                    file_type=ft.FilePickerFileType.IMAGE,
                    allow_multiple=False,
                )

                if not files or not files[0].path:
                    return

                channel_avatar["path"] = files[0].path

                avatar_preview.content = ft.Image(
                    src=files[0].path,
                    width=85,
                    height=85,
                    fit=ft.BoxFit.COVER,
                )
                avatar_preview.update()

            except Exception as ex:
                notify(f"Ошибка: {ex}")

        def save(ev):
            channel_name = (name.value or "").strip()
            channel_username = (
                (username.value or "").strip().lstrip("@")
            )

            if not channel_name:
                notify("Введи название канала")
                return

            if visibility.value == "Публичный" and not channel_username:
                notify("Публичному каналу нужен username")
                return

            if channel_username and not channel_username.replace("_", "").isalnum():
                notify("Username может содержать буквы, цифры и _")
                return

            if channel_username and any(
                c["username"].lower() == channel_username.lower()
                for c in state["channels"]
                if c["username"]
            ):
                notify("Такой username уже занят")
                return

            channel = {
                "id": str(len(state["channels"]) + 1),
                "name": channel_name,
                "username": channel_username,
                "description": (description.value or "").strip(),
                "visibility": visibility.value,
                "avatar": channel_avatar["path"],
                "subscribers": 1,
                "posts": [],
            }

            state["channels"].append(channel)
            page.pop_dialog()
            state["selected_channel"] = channel
            render()
            notify("Канал создан!")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=txt("Создать канал", 21),
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    avatar_preview,
                                    outline_button(
                                        "Выбрать аватар",
                                        choose_channel_avatar,
                                        ft.Icons.CAMERA_ALT_OUTLINED,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ),
                        name,
                        username,
                        description,
                        visibility,
                        txt(
                            "Публичный канал можно будет находить "
                            "по username. Приватный предназначен "
                            "для приглашений.",
                            11,
                            C["muted"],
                        ),
                    ],
                    tight=True,
                    width=310,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.TextButton("Создать", on_click=save),
                ],
            )
        )

    # ==========================================
    # CHANNEL DETAIL
    # ==========================================
    def open_channel(channel):
        state["selected_channel"] = channel
        render()

    def channel_detail_screen():
        channel = state["selected_channel"]

        if not channel:
            return channels_screen()

        avatar = (
            ft.Image(
                src=channel["avatar"],
                width=90,
                height=90,
                fit=ft.BoxFit.COVER,
            )
            if channel["avatar"]
            else ft.Icon(
                ft.Icons.CAMPAIGN,
                size=48,
                color=C["cyan"],
            )
        )

        posts = channel["posts"]

        controls = [
            ft.Row(
                [
                    ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        icon_color=C["cyan"],
                        on_click=lambda e: back_to_channels(),
                    ),
                    txt("Канал", 21, weight=ft.FontWeight.BOLD),
                ]
            ),
            panel(
                ft.Column(
                    [
                        ft.Container(
                            content=avatar,
                            width=90,
                            height=90,
                            alignment=ft.Alignment.CENTER,
                            border_radius=50,
                            bgcolor="#25213F",
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                        txt(channel["name"], 22, weight=ft.FontWeight.BOLD),
                        txt(
                            "@" + channel["username"]
                            if channel["username"]
                            else "Приватный канал",
                            13,
                            C["cyan"],
                        ),
                        txt(
                            channel["description"] or "Описание отсутствует",
                            13,
                            C["muted"],
                        ),
                        txt(
                            f'{channel["subscribers"]} подписчик(ов)',
                            12,
                            C["muted"],
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=9,
                )
            ),
            button(
                "Опубликовать сообщение",
                create_post,
                ft.Icons.EDIT,
            ),
            txt("Публикации", 18, weight=ft.FontWeight.BOLD),
        ]

        if not posts:
            controls.append(
                empty(
                    ft.Icons.ARTICLE_OUTLINED,
                    "Публикаций пока нет",
                    "Здесь будут отображаться сообщения канала.",
                )
            )
        else:
            for post in reversed(posts):
                controls.append(
                    panel(
                        ft.Column(
                            [
                                txt(post, 15),
                                txt("Публикация канала", 11, C["muted"]),
                            ],
                            spacing=7,
                        )
                    )
                )

        return ft.Column(
            controls,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    def back_to_channels():
        state["selected_channel"] = None
        render()

    def create_post(e):
        channel = state["selected_channel"]
        post_field = field("Сообщение", "Напиши публикацию...")

        def publish(ev):
            value = (post_field.value or "").strip()

            if not value:
                notify("Сообщение пустое")
                return

            channel["posts"].append(value)
            page.pop_dialog()
            render()
            notify("Публикация добавлена")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=txt("Новая публикация"),
                content=ft.Column(
                    [post_field],
                    tight=True,
                    width=300,
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.TextButton("Опубликовать", on_click=publish),
                ],
            )
        )

    # ==========================================
    # CHANNELS
    # ==========================================
    def channels_screen():
        controls = [
            heading("Каналы", "Новости, публикации и сообщества"),
            button(
                "Создать канал",
                create_channel,
                ft.Icons.ADD,
            ),
        ]

        if not state["channels"]:
            controls.append(
                empty(
                    ft.Icons.CAMPAIGN_OUTLINED,
                    "Каналов пока нет",
                    "Создай свой первый канал VibeGram.",
                )
            )
        else:
            for channel in state["channels"]:
                avatar = (
                    ft.Image(
                        src=channel["avatar"],
                        width=55,
                        height=55,
                        fit=ft.BoxFit.COVER,
                    )
                    if channel["avatar"]
                    else ft.Icon(
                        ft.Icons.CAMPAIGN,
                        size=28,
                        color=C["cyan"],
                    )
                )

                controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=avatar,
                                    width=55,
                                    height=55,
                                    border_radius=50,
                                    bgcolor="#25213F",
                                    alignment=ft.Alignment.CENTER,
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                ),
                                ft.Column(
                                    [
                                        txt(
                                            channel["name"],
                                            15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        txt(
                                            channel["description"] or "Канал VibeGram",
                                            12,
                                            C["muted"],
                                        ),
                                        txt(
                                            channel["visibility"],
                                            11,
                                            C["cyan"],
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                ft.Icon(
                                    ft.Icons.CHEVRON_RIGHT,
                                    color=C["muted"],
                                ),
                            ],
                            spacing=12,
                        ),
                        padding=14,
                        bgcolor=C["panel"],
                        border=ft.Border.all(1, C["border"]),
                        border_radius=17,
                        on_click=lambda e, ch=channel: open_channel(ch),
                        ink=True,
                    )
                )

        return ft.Column(
            controls,
            expand=True,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    # ==========================================
    # GROUPS
    # ==========================================
    def create_group(e):
        name = field("Название группы", "Например, Друзья")
        description = field("Описание", "О чём группа?")

        def save(ev):
            value = (name.value or "").strip()

            if not value:
                notify("Введи название группы")
                return

            state["groups"].append({
                "name": value,
                "description": (description.value or "").strip(),
            })

            page.pop_dialog()
            render()
            notify("Группа создана")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=txt("Новая группа"),
                content=ft.Column(
                    [name, description],
                    tight=True,
                    width=300,
                    spacing=10,
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.TextButton("Создать", on_click=save),
                ],
            )
        )

    def groups_screen():
        controls = [
            heading("Группы", "Общайся сразу с несколькими людьми"),
            button("Создать группу", create_group, ft.Icons.GROUP_ADD),
        ]

        if not state["groups"]:
            controls.append(
                empty(
                    ft.Icons.GROUP_OUTLINED,
                    "Групп пока нет",
                    "Создай первую группу.",
                )
            )

        for group in state["groups"]:
            controls.append(
                panel(
                    ft.Column(
                        [
                            txt(group["name"], 16, weight=ft.FontWeight.BOLD),
                            txt(group["description"], 12, C["muted"]),
                        ],
                        spacing=5,
                    )
                )
            )

        return ft.Column(
            controls,
            expand=True,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    # ==========================================
    # CHATS
    # ==========================================
    def chats_screen():
        search = field("Поиск", "Найти переписку или пользователя")

        controls = [
            heading("Чаты", "Твои личные переписки"),
            search,
            ft.Row(
                [
                    outline_button(
                        "Папки",
                        lambda e: open_subpage("folders"),
                        ft.Icons.FOLDER_OUTLINED,
                    ),
                    outline_button(
                        "Настройки",
                        lambda e: open_subpage("chat_settings"),
                        ft.Icons.TUNE,
                    ),
                ],
                wrap=True,
            ),
            empty(
                ft.Icons.CHAT_BUBBLE_OUTLINE,
                "Пока нет чатов",
                "Когда появятся переписки, они будут здесь.",
            ),
        ]

        return ft.Column(
            controls,
            expand=True,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    # ==========================================
    # CONTACTS
    # ==========================================
    def contacts_screen():
        return ft.Column(
            [
                heading("Контакты", "Находи людей в VibeGram"),
                panel(
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PERSON_SEARCH,
                                size=30,
                                color=C["cyan"],
                            ),
                            ft.Column(
                                [
                                    txt("Поиск пользователей", 15,
                                        weight=ft.FontWeight.BOLD),
                                    txt("Поиск по username", 12, C["muted"]),
                                ],
                                expand=True,
                            ),
                        ]
                    )
                ),
                button(
                    "Найти пользователей",
                    lambda e: notify("Поиск подключим к Firestore"),
                    ft.Icons.SEARCH,
                ),
                empty(
                    ft.Icons.PEOPLE_OUTLINE,
                    "Контактов пока нет",
                    "Здесь появятся твои контакты.",
                ),
            ],
            expand=True,
            spacing=12,
        )

    # ==========================================
    # SETTINGS HELPERS
    # ==========================================
    def open_subpage(name):
        state["subpage"] = name
        render()

    def back_subpage(e):
        state["subpage"] = None
        render()

    def setting_switch(title, subtitle, key):
        return panel(
            ft.Row(
                [
                    ft.Column(
                        [
                            txt(title, 14, weight=ft.FontWeight.BOLD),
                            txt(subtitle, 11, C["muted"]),
                        ],
                        expand=True,
                        spacing=4,
                    ),
                    ft.Switch(
                        value=state[key],
                        active_color=C["purple"],
                        on_change=lambda e: update_setting(key, e.control.value),
                    ),
                ]
            )
        )

    def update_setting(key, value):
        state[key] = value
        notify("Настройка изменена")

    def subpage(title, subtitle, controls):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            icon_color=C["cyan"],
                            on_click=back_subpage,
                        ),
                        heading(title, subtitle),
                    ]
                ),
                *controls,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    # ==========================================
    # SUBPAGES
    # ==========================================
    def privacy_screen():
        return subpage(
            "Приватность",
            "Управляй своей видимостью",
            [
                setting_switch("Статус онлайн", "Показывать статус",
                               "show_online"),
                setting_switch("Номер телефона", "Показывать номер",
                               "show_phone"),
                setting_switch("Фото профиля", "Показывать аватар",
                               "show_photo"),
                setting_switch("Личные сообщения", "Разрешить сообщения",
                               "allow_messages"),
                setting_switch("Добавление в группы", "Разрешить добавление",
                               "allow_groups"),
                setting_switch("Отчёты о прочтении", "Статус прочтения",
                               "read_receipts"),
            ],
        )

    def notifications_screen():
        return subpage(
            "Уведомления",
            "Настрой уведомления",
            [
                setting_switch("Все уведомления", "Главный переключатель",
                               "notifications"),
                setting_switch("Личные сообщения", "Уведомления из чатов",
                               "message_notifications"),
                setting_switch("Группы", "Уведомления из групп",
                               "group_notifications"),
                setting_switch("Каналы", "Уведомления из каналов",
                               "channel_notifications"),
                setting_switch("Звуки", "Звуковое сопровождение",
                               "sound"),
                setting_switch("Вибрация", "Вибрация устройства",
                               "vibration"),
                txt(
                    "Настоящие push-уведомления подключим через Firebase Cloud Messaging.",
                    12,
                    C["muted"],
                ),
            ],
        )

    def plus_screen():
        return subpage(
            "Vibe+",
            "Премиальные возможности",
            [
                panel(
                    ft.Column(
                        [
                            txt("✦ VIBE+", 32, "#C5A4FF",
                                ft.FontWeight.BOLD),
                            txt("Больше возможностей. Больше индивидуальности.",
                                13, C["muted"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ),
                section(ft.Icons.PALETTE, "Эксклюзивные темы",
                        "Особые темы оформления", lambda e: None),
                section(ft.Icons.STAR, "Значок Vibe+",
                        "Премиальный значок", lambda e: None),
                section(ft.Icons.MOOD, "Дополнительные реакции",
                        "Больше реакций", lambda e: None),
                button(
                    "Включить деморежим Vibe+",
                    activate_plus,
                    ft.Icons.STARS,
                ),
                txt(
                    "Демонстрационный режим. Настоящую подписку "
                    "подключим через сервер.",
                    12,
                    C["muted"],
                ),
            ],
        )

    def activate_plus(e):
        state["vibe_plus"] = not state["vibe_plus"]
        notify(
            "Демонстрационный Vibe+ включён"
            if state["vibe_plus"]
            else "Vibe+ выключен"
        )
        render()

    def folders_screen():
        def create_folder(e):
            name = field("Название папки", "Например, Друзья")

            def save(ev):
                value = (name.value or "").strip()

                if not value:
                    notify("Введи название")
                    return

                state["folders"].append(value)
                page.pop_dialog()
                render()
                notify("Папка создана")

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    title=txt("Новая папка"),
                    content=name,
                    actions=[
                        ft.TextButton(
                            "Отмена",
                            on_click=lambda e: page.pop_dialog(),
                        ),
                        ft.TextButton("Создать", on_click=save),
                    ],
                )
            )

        controls = [
            button(
                "Создать папку",
                create_folder,
                ft.Icons.CREATE_NEW_FOLDER,
            )
        ]

        for folder in state["folders"]:
            controls.append(
                panel(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.FOLDER, color=C["cyan"]),
                            txt(folder, 15),
                        ]
                    )
                )
            )

        if not state["folders"]:
            controls.append(
                empty(
                    ft.Icons.FOLDER_OUTLINED,
                    "Папок пока нет",
                    "Создай папку для переписок.",
                )
            )

        return subpage(
            "Папки чатов",
            "Организация переписок",
            controls,
        )

    def chat_settings_screen():
        font = ft.Dropdown(
            label="Размер текста",
            value=state["font_size"],
            options=[
                ft.dropdown.Option("Маленький"),
                ft.dropdown.Option("Средний"),
                ft.dropdown.Option("Большой"),
            ],
        )

        wallpaper = ft.Dropdown(
            label="Обои чатов",
            value=state["chat_wallpaper"],
            options=[
                ft.dropdown.Option("Стандартные"),
                ft.dropdown.Option("Тёмные"),
                ft.dropdown.Option("Фиолетовые"),
                ft.dropdown.Option("Синие"),
            ],
        )

        def save(e):
            state["font_size"] = font.value
            state["chat_wallpaper"] = wallpaper.value
            notify("Настройки сохранены")
            render()

        return subpage(
            "Настройки чатов",
            "Персонализируй переписки",
            [
                panel(
                    ft.Column(
                        [
                            font,
                            wallpaper,
                            button("Сохранить", save),
                        ],
                        spacing=12,
                    )
                ),
                setting_switch(
                    "Автозагрузка медиа",
                    "Автоматическая загрузка",
                    "auto_download",
                ),
                setting_switch(
                    "Отчёты о прочтении",
                    "Показывать прочтение",
                    "read_receipts",
                ),
            ],
        )

    def language_screen():
        dropdown = ft.Dropdown(
            label="Язык",
            value=state["language"],
            options=[
                ft.dropdown.Option(x)
                for x in [
                    "Русский", "English", "Polski",
                    "Українська", "Deutsch", "Español",
                ]
            ],
        )

        def save(e):
            state["language"] = dropdown.value
            notify("Язык выбран")
            render()

        return subpage(
            "Язык",
            "Выбери язык приложения",
            [
                panel(
                    ft.Column(
                        [
                            dropdown,
                            button("Сохранить", save),
                        ],
                        spacing=12,
                    )
                )
            ],
        )

    def appearance_screen():
        def change_theme(e):
            if state["theme"] == "dark":
                state["theme"] = "light"
                page.theme_mode = ft.ThemeMode.LIGHT
                page.bgcolor = "#F4F2FF"
                C.update({
                    "bg": "#F4F2FF",
                    "panel": "#FFFFFF",
                    "panel2": "#EEEEF8",
                    "text": "#17152A",
                    "muted": "#77738D",
                    "border": "#DDD9EA",
                })
            else:
                state["theme"] = "dark"
                page.theme_mode = ft.ThemeMode.DARK
                page.bgcolor = "#090914"
                C.update({
                    "bg": "#090914",
                    "panel": "#141426",
                    "panel2": "#1D1B35",
                    "text": "#F5F3FF",
                    "muted": "#9292AC",
                    "border": "#292944",
                })

            render()

        return subpage(
            "Оформление",
            "Настрой внешний вид",
            [
                button(
                    "Сменить тему",
                    change_theme,
                    ft.Icons.PALETTE_OUTLINED,
                ),
            ],
        )

    def about_screen():
        return subpage(
            "О приложении",
            "Информация о VibeGram",
            [
                panel(
                    ft.Column(
                        [
                            txt("V", 48, C["purple"], ft.FontWeight.BOLD),
                            txt("VibeGram", 25, weight=ft.FontWeight.BOLD),
                            txt("Общайся. Создавай. Будь собой.",
                                13, C["muted"]),
                            txt("Версия 1.0", 12, C["cyan"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
            ],
        )

    # ==========================================
    # SETTINGS SCREEN
    # ==========================================
    def settings_screen():
        return ft.Column(
            [
                heading("Настройки", "Управляй своим VibeGram"),
                section(ft.Icons.LANGUAGE, "Язык", state["language"],
                        lambda e: open_subpage("language")),
                section(ft.Icons.CHAT_OUTLINED, "Настройки чатов",
                        "Текст и обои", lambda e: open_subpage("chat_settings")),
                section(ft.Icons.FOLDER_OUTLINED, "Папки чатов",
                        "Управление папками", lambda e: open_subpage("folders")),
                section(ft.Icons.NOTIFICATIONS_OUTLINED, "Уведомления",
                        "Звуки и сообщения", lambda e: open_subpage("notifications")),
                section(ft.Icons.SHIELD_OUTLINED, "Приватность",
                        "Безопасность", lambda e: open_subpage("privacy")),
                section(ft.Icons.PALETTE_OUTLINED, "Оформление",
                        "Темы приложения", lambda e: open_subpage("appearance")),
                section(ft.Icons.STAR, "Vibe+",
                        "Премиум", lambda e: open_subpage("plus")),
                section(ft.Icons.INFO_OUTLINE, "О приложении",
                        "Информация", lambda e: open_subpage("about")),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    # ==========================================
    # NAVIGATION
    # ==========================================
    nav = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        spacing=0,
    )

    def set_tab(tab):
        state["tab"] = tab
        state["subpage"] = None
        state["selected_channel"] = None
        render()

    def create_nav():
        nav.controls.clear()

        items = [
            ("Чаты", ft.Icons.CHAT_BUBBLE_OUTLINE),
            ("Контакты", ft.Icons.PEOPLE_OUTLINE),
            ("Каналы", ft.Icons.CAMPAIGN_OUTLINED),
            ("Группы", ft.Icons.GROUP_OUTLINED),
            ("Профиль", ft.Icons.PERSON_OUTLINE),
        ]

        for label, icon in items:
            active = state["tab"] == label

            nav.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                icon,
                                size=22,
                                color=C["cyan"] if active else C["muted"],
                            ),
                            txt(
                                label,
                                10,
                                C["cyan"] if active else C["muted"],
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=3,
                    ),
                    padding=ft.Padding.symmetric(vertical=9, horizontal=3),
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    on_click=lambda e, t=label: set_tab(t),
                    ink=True,
                )
            )

    # ==========================================
    # MAIN RENDER
    # ==========================================
    def render():
        page.clean()

        if state["auth_loading"]:
            page.add(
                ft.SafeArea(
                    content=ft.Container(
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Column(
                            [
                                ft.ProgressRing(
                                    color=C["purple"],
                                    width=45,
                                    height=45,
                                ),
                                txt(
                                    "Подключаем VibeGram...",
                                    16,
                                    C["muted"],
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                        ),
                    ),
                    expand=True,
                )
            )
            page.update()
            return

        if not state["authenticated"]:
            page.add(
                ft.SafeArea(
                    content=auth_screen(),
                    expand=True,
                )
            )
            page.update()
            return

        create_nav()

        subpages = {
            "privacy": privacy_screen,
            "notifications": notifications_screen,
            "plus": plus_screen,
            "folders": folders_screen,
            "chat_settings": chat_settings_screen,
            "language": language_screen,
            "appearance": appearance_screen,
            "about": about_screen,
        }

        if state["selected_channel"]:
            screen = channel_detail_screen()
        elif state["subpage"] in subpages:
            screen = subpages[state["subpage"]]()
        else:
            screens = {
                "Чаты": chats_screen,
                "Контакты": contacts_screen,
                "Каналы": channels_screen,
                "Группы": groups_screen,
                "Профиль": profile_screen,
                "Настройки": settings_screen,
            }

            screen = screens.get(state["tab"], chats_screen)()

        header = ft.Container(
            padding=ft.Padding.symmetric(horizontal=18, vertical=8),
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=txt(
                                    "V", 21, "white",
                                    ft.FontWeight.BOLD,
                                ),
                                width=39,
                                height=39,
                                alignment=ft.Alignment.CENTER,
                                border_radius=13,
                                gradient=ft.LinearGradient(
                                    colors=[C["purple"], C["blue"]],
                                ),
                            ),
                            txt("VibeGram", 19,
                                weight=ft.FontWeight.BOLD),
                        ],
                        spacing=9,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.STAR,
                                icon_color="#C5A4FF",
                                tooltip="Vibe+",
                                on_click=lambda e: open_subpage("plus"),
                            ),
                            ft.IconButton(
                                ft.Icons.SETTINGS_OUTLINED,
                                icon_color=C["muted"],
                                tooltip="Настройки",
                                on_click=lambda e: set_tab("Настройки"),
                            ),
                        ],
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        body = ft.Container(
            content=screen,
            padding=ft.Padding.symmetric(horizontal=18, vertical=12),
            expand=True,
        )

        bottom = ft.Container(
            content=nav,
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            padding=ft.Padding.symmetric(horizontal=4, vertical=2),
        )

        page.add(
            ft.SafeArea(
                content=ft.Column(
                    [
                        header,
                        body,
                        bottom,
                    ],
                    expand=True,
                    spacing=0,
                ),
                expand=True,
            )
        )

        page.update()

    # ==========================================
    # START
    # ==========================================
    render()
    page.run_task(restore_auth)


ft.app(target=main)
