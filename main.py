
import flet as ft
from flet_firebase_auth import FirebaseAuth


def main(page: ft.Page):
    # -----------------------------
    # СЕРВИСЫ
    # -----------------------------
    firebase_auth = FirebaseAuth()
    page.services.append(firebase_auth)

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # -----------------------------
    # ОСНОВНЫЕ НАСТРОЙКИ
    # -----------------------------
    page.title = "VibeGram"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#090914"
    page.padding = 0
    page.spacing = 0

    C = {
        "bg": "#090914",
        "panel": "#141426",
        "panel2": "#1B1B32",
        "purple": "#8B5CF6",
        "blue": "#3B82F6",
        "cyan": "#22D3EE",
        "text": "#F5F3FF",
        "muted": "#9292AC",
        "border": "#292944",
        "danger": "#F87171",
    }

    state = {
        "tab": "Чаты",
        "subpage": None,
        "theme": "dark",

        "username": "",
        "display_name": "",
        "about": "",
        "avatar": None,
        "profile_bg": None,

        "groups": [],
        "channels": [],
        "messages": {},
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

        "language": "Русский",
        "font_size": "Средний",
        "chat_wallpaper": "Стандартные",
        "auto_download": True,
        "read_receipts": True,

        "uid": "",
        "email": "",
        "is_signed_in": False,

        "vibe_plus": False,
        "plus_features": {
            "exclusive_themes": True,
            "premium_badge": True,
            "animated_avatar": True,
            "extra_reactions": True,
            "advanced_folders": True,
        },
    }

    nav = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        spacing=0,
    )

    # -----------------------------
    # ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    # -----------------------------
    def text(value, size=14, color=None, weight=None):
        return ft.Text(
            str(value),
            size=size,
            color=color or C["text"],
            weight=weight,
        )

    def panel(control, padding=16):
        return ft.Container(
            content=control,
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            border_radius=18,
            padding=padding,
        )

    def neon_button(label, on_click, icon=None):
        return ft.ElevatedButton(
            content=ft.Text(label),
            icon=icon,
            on_click=on_click,
            bgcolor=C["purple"],
            color="white",
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
            ),
        )

    def secondary_button(label, on_click, icon=None):
        return ft.OutlinedButton(
            content=ft.Text(label),
            icon=icon,
            on_click=on_click,
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
            border_color=C["border"],
            focused_border_color=C["purple"],
            color=C["text"],
            bgcolor=C["panel"],
            border_radius=12,
        )

    def notify(message):
        page.snack_bar = ft.SnackBar(content=text(message))
        page.snack_bar.open = True
        page.update()

    def heading(title, subtitle=None):
        controls = [
            text(title, 25, weight=ft.FontWeight.BOLD)
        ]
        if subtitle:
            controls.append(text(subtitle, 13, C["muted"]))

        return ft.Column(controls, spacing=5)

    def empty_state(icon, title, subtitle):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=25,
            content=ft.Column(
                [
                    ft.Icon(icon, size=58, color=C["purple"]),
                    text(title, 19, weight=ft.FontWeight.BOLD),
                    text(subtitle, 13, C["muted"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
        )

    def section_card(icon, title, subtitle, on_click):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            icon,
                            color=C["cyan"],
                            size=25,
                        ),
                        bgcolor="#25213F",
                        padding=13,
                        border_radius=14,
                    ),
                    ft.Column(
                        [
                            text(title, 15, weight=ft.FontWeight.BOLD),
                            text(subtitle, 12, C["muted"]),
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
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            border_radius=18,
            padding=16,
            on_click=on_click,
            ink=True,
        )

    def setting_switch(title, subtitle, key):
        return panel(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    text(title, 15, weight=ft.FontWeight.BOLD),
                                    text(subtitle, 12, C["muted"]),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Switch(
                                value=state[key],
                                active_color=C["purple"],
                                on_change=lambda e: change_setting(
                                    key, e.control.value
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                ],
                spacing=5,
            )
        )

    def change_setting(key, value):
        state[key] = value
        notify("Настройка изменена")

    # -----------------------------
    # GOOGLE АВТОРИЗАЦИЯ
    # -----------------------------
    async def google_sign_in(e):
        try:
            result = await firebase_auth.sign_in()

            if not isinstance(result, dict):
                notify("Не удалось получить ответ от Firebase")
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
            state["is_signed_in"] = True

            notify("Вход через Google выполнен!")
            render()

        except Exception as ex:
            notify(f"Ошибка Google-входа: {ex}")

    async def google_sign_out(e):
        try:
            result = await firebase_auth.sign_out()

            if isinstance(result, dict) and not result.get("success"):
                notify(str(result.get("error", "Ошибка выхода")))
                return

            state["uid"] = ""
            state["email"] = ""
            state["is_signed_in"] = False

            notify("Ты вышел из аккаунта")
            render()

        except Exception as ex:
            notify(f"Ошибка выхода: {ex}")

    # -----------------------------
    # ИЗОБРАЖЕНИЯ
    # -----------------------------
    async def pick_image(image_type):
        try:
            files = await file_picker.pick_files(
                dialog_title="Выбери изображение",
                file_type=ft.FilePickerFileType.IMAGE,
                allow_multiple=False,
            )

            if not files:
                return

            selected = files[0]

            if not selected.path:
                notify("Не удалось получить путь к изображению")
                return

            if image_type == "avatar":
                state["avatar"] = selected.path
                notify("Аватар изменён")

            elif image_type == "background":
                state["profile_bg"] = selected.path
                notify("Фон профиля изменён")

            render()

        except Exception as ex:
            notify(f"Ошибка выбора изображения: {ex}")

    async def choose_avatar(e):
        await pick_image("avatar")

    async def choose_background(e):
        await pick_image("background")

    # -----------------------------
    # РЕДАКТИРОВАНИЕ ПРОФИЛЯ
    # -----------------------------
    def edit_profile():
        name = field("Имя", "Твоё имя", state["display_name"])
        username = field(
            "Username", "Например, vibe_user", state["username"]
        )
        about = field(
            "О себе", "Расскажи немного о себе", state["about"]
        )

        def save(e):
            new_username = (
                username.value or ""
            ).strip().lstrip("@")

            if not new_username:
                notify("Username не может быть пустым")
                return

            state["display_name"] = (name.value or "").strip()
            state["username"] = new_username
            state["about"] = (about.value or "").strip()

            page.pop_dialog()
            render()
            notify("Профиль обновлён")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=text("Изменить профиль", 21),
                content=ft.Column(
                    [name, username, about],
                    tight=True,
                    spacing=12,
                    width=300,
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

    # -----------------------------
    # ПРОФИЛЬ
    # -----------------------------
    def profile_screen():
        if state["avatar"]:
            avatar = ft.Container(
                content=ft.Image(
                    src=state["avatar"],
                    width=112,
                    height=112,
                    fit=ft.BoxFit.COVER,
                ),
                width=112,
                height=112,
                border_radius=60,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                border=ft.Border.all(3, C["cyan"]),
            )
        else:
            avatar = ft.Container(
                content=ft.Icon(
                    ft.Icons.PERSON,
                    size=58,
                    color=C["cyan"],
                ),
                width=112,
                height=112,
                bgcolor="#25213F",
                border_radius=60,
                alignment=ft.Alignment.CENTER,
                border=ft.Border.all(3, C["cyan"]),
            )

        profile_content = ft.Column(
            [
                avatar,
                text(
                    state["display_name"] or "Твоё имя",
                    23,
                    weight=ft.FontWeight.BOLD,
                ),
                text(
                    "@" + state["username"]
                    if state["username"]
                    else "@username",
                    14,
                    C["muted"],
                ),
                text(
                    state["about"] or "Расскажи о себе",
                    13,
                    C["muted"],
                ),
                text(
                    "Vibe+ ✦" if state["vibe_plus"] else "",
                    13,
                    "#C5A4FF",
                    ft.FontWeight.BOLD,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        if state["profile_bg"]:
            background = ft.Image(
                src=state["profile_bg"],
                width=500,
                height=280,
                fit=ft.BoxFit.COVER,
            )
        else:
            background = ft.Container(
                bgcolor="#1B1B32",
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=["#29204F", "#17172E", "#102B40"],
                ),
            )

        profile_banner = ft.Container(
            content=ft.Stack(
                [
                    background,
                    ft.Container(
                        content=profile_content,
                        alignment=ft.Alignment.CENTER,
                        bgcolor="#99090914",
                        expand=True,
                    ),
                ]
            ),
            height=280,
            border_radius=22,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.Border.all(1, C["border"]),
        )

        auth_controls = []

        if state["is_signed_in"]:
            auth_controls.extend([
                panel(
                    ft.Column(
                        [
                            text("Аккаунт Google", 15,
                                 weight=ft.FontWeight.BOLD),
                            text(state["email"], 12, C["muted"]),
                            text("Аккаунт подключён", 12, "#22C55E"),
                        ],
                        spacing=5,
                    )
                ),
                secondary_button(
                    "Выйти из аккаунта",
                    google_sign_out,
                    ft.Icons.LOGOUT,
                ),
            ])
        else:
            auth_controls.append(
                neon_button(
                    "Продолжить с Google",
                    google_sign_in,
                    ft.Icons.LOGIN,
                )
            )

        return ft.Column(
            [
                heading("Профиль", "Твоя страница VibeGram"),
                ft.Container(height=8),
                profile_banner,
                ft.Row(
                    [
                        ft.Container(
                            content=secondary_button(
                                "Аватар",
                                choose_avatar,
                                ft.Icons.CAMERA_ALT_OUTLINED,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=secondary_button(
                                "Фон",
                                choose_background,
                                ft.Icons.IMAGE_OUTLINED,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=8,
                ),
                neon_button(
                    "Изменить профиль",
                    lambda e: edit_profile(),
                    ft.Icons.EDIT_OUTLINED,
                ),
                *auth_controls,
                section_card(
                    ft.Icons.STAR,
                    "Vibe+",
                    "Премиальные возможности VibeGram",
                    lambda e: open_subpage("plus"),
                ),
                section_card(
                    ft.Icons.SHIELD_OUTLINED,
                    "Приватность",
                    "Настройки безопасности и видимости",
                    lambda e: open_subpage("privacy"),
                ),
                section_card(
                    ft.Icons.NOTIFICATIONS_OUTLINED,
                    "Уведомления",
                    "Настройка уведомлений",
                    lambda e: open_subpage("notifications"),
                ),
                section_card(
                    ft.Icons.INFO_OUTLINE,
                    "О приложении",
                    "VibeGram — общайся без границ",
                    lambda e: open_subpage("about"),
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    # -----------------------------
    # ПОДРАЗДЕЛЫ
    # -----------------------------
    def open_subpage(name):
        state["subpage"] = name
        render()

    def back_to_profile(e):
        state["subpage"] = None
        render()

    def subpage_screen(title, subtitle, controls):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            icon_color=C["cyan"],
                            on_click=back_to_profile,
                        ),
                        heading(title, subtitle),
                    ],
                    spacing=8,
                ),
                ft.Container(height=12),
                *controls,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # -----------------------------
    # VIBE+
    # -----------------------------
    def plus_screen():
        features = [
            ("Эксклюзивные темы", "Особые темы оформления",
             "exclusive_themes"),
            ("Значок Vibe+", "Премиальный значок возле имени",
             "premium_badge"),
            ("Анимированный аватар", "Дополнительное оформление профиля",
             "animated_avatar"),
            ("Дополнительные реакции", "Больше вариантов реакций",
             "extra_reactions"),
            ("Расширенные папки", "Дополнительные возможности папок",
             "advanced_folders"),
        ]

        controls = [
            panel(
                ft.Column(
                    [
                        text("✦ VIBE+", 32, "#C5A4FF",
                             ft.FontWeight.BOLD),
                        text(
                            "Больше возможностей. Больше индивидуальности.",
                            13,
                            C["muted"],
                        ),
                        text(
                            "Премиальные функции VibeGram",
                            15,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                )
            )
        ]

        for title, subtitle, key in features:
            controls.append(
                panel(
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    text(title, 15,
                                         weight=ft.FontWeight.BOLD),
                                    text(subtitle, 12, C["muted"]),
                                ],
                                expand=True,
                                spacing=4,
                            ),
                            ft.Icon(
                                ft.Icons.STAR,
                                color="#C5A4FF",
                            ),
                        ]
                    )
                )
            )

        controls.extend([
            neon_button(
                "Включить демонстрационный Vibe+",
                activate_plus,
                ft.Icons.STARS,
            ),
            text(
                "Сейчас это демонстрационный режим. "
                "Настоящую подписку, оплату и проверку доступа "
                "подключим через сервер.",
                12,
                C["muted"],
            ),
        ])

        return subpage_screen(
            "Vibe+",
            "Премиум-подписка VibeGram",
            controls,
        )

    def activate_plus(e):
        state["vibe_plus"] = not state["vibe_plus"]
        notify(
            "Демонстрационный Vibe+ включён"
            if state["vibe_plus"]
            else "Демонстрационный Vibe+ выключен"
        )
        render()

    # -----------------------------
    # ПРИВАТНОСТЬ
    # -----------------------------
    def privacy_screen():
        return subpage_screen(
            "Приватность",
            "Управляй видимостью профиля",
            [
                setting_switch(
                    "Показывать статус онлайн",
                    "Другие пользователи смогут видеть, когда ты в сети",
                    "show_online",
                ),
                setting_switch(
                    "Показывать номер телефона",
                    "Разрешить другим видеть номер телефона",
                    "show_phone",
                ),
                setting_switch(
                    "Показывать фотографию профиля",
                    "Разрешить другим пользователям видеть аватар",
                    "show_photo",
                ),
                setting_switch(
                    "Разрешить сообщения",
                    "Разрешить пользователям писать тебе",
                    "allow_messages",
                ),
                setting_switch(
                    "Добавление в группы",
                    "Разрешить добавлять тебя в группы",
                    "allow_groups",
                ),
                setting_switch(
                    "Отчёты о прочтении",
                    "Показывать статус прочтения сообщений",
                    "read_receipts",
                ),
                panel(
                    ft.Column(
                        [
                            text("Дополнительная безопасность", 15,
                                 weight=ft.FontWeight.BOLD),
                            text(
                                "Активные сеансы, блокировки и "
                                "двухэтапную проверку добавим при "
                                "подключении серверной части.",
                                12,
                                C["muted"],
                            ),
                        ],
                        spacing=7,
                    )
                ),
            ],
        )

    # -----------------------------
    # УВЕДОМЛЕНИЯ
    # -----------------------------
    def notifications_screen():
        return subpage_screen(
            "Уведомления",
            "Настрой уведомления VibeGram",
            [
                setting_switch(
                    "Все уведомления",
                    "Главный переключатель уведомлений",
                    "notifications",
                ),
                setting_switch(
                    "Личные сообщения",
                    "Уведомления из личных чатов",
                    "message_notifications",
                ),
                setting_switch(
                    "Группы",
                    "Уведомления из групповых чатов",
                    "group_notifications",
                ),
                setting_switch(
                    "Каналы",
                    "Уведомления из каналов",
                    "channel_notifications",
                ),
                setting_switch(
                    "Звуки",
                    "Звуковое сопровождение уведомлений",
                    "sound",
                ),
                setting_switch(
                    "Вибрация",
                    "Вибрация при новых уведомлениях",
                    "vibration",
                ),
                text(
                    "Для настоящих push-уведомлений подключим "
                    "Firebase Cloud Messaging.",
                    12,
                    C["muted"],
                ),
            ],
        )

    # -----------------------------
    # ЯЗЫК
    # -----------------------------
    def language_screen():
        languages = [
            "Русский",
            "English",
            "Polski",
            "Українська",
            "Deutsch",
            "Español",
            "Français",
        ]

        dropdown = ft.Dropdown(
            label="Язык приложения",
            value=state["language"],
            options=[
                ft.dropdown.Option(language)
                for language in languages
            ],
            border_color=C["border"],
            color=C["text"],
        )

        def save(e):
            state["language"] = dropdown.value
            notify(
                "Язык выбран. Перевод всех экранов подключим отдельно."
            )
            render()

        return subpage_screen(
            "Язык",
            "Выбери язык VibeGram",
            [
                panel(
                    ft.Column(
                        [
                            text("Язык приложения", 16,
                                 weight=ft.FontWeight.BOLD),
                            dropdown,
                            neon_button("Сохранить", save),
                        ],
                        spacing=12,
                    )
                )
            ],
        )

    # -----------------------------
    # НАСТРОЙКИ ЧАТОВ
    # -----------------------------
    def chat_settings_screen():
        font_dropdown = ft.Dropdown(
            label="Размер текста",
            value=state["font_size"],
            options=[
                ft.dropdown.Option("Маленький"),
                ft.dropdown.Option("Средний"),
                ft.dropdown.Option("Большой"),
            ],
            border_color=C["border"],
        )

        wallpaper_dropdown = ft.Dropdown(
            label="Обои чатов",
            value=state["chat_wallpaper"],
            options=[
                ft.dropdown.Option("Стандартные"),
                ft.dropdown.Option("Тёмные"),
                ft.dropdown.Option("Фиолетовые"),
                ft.dropdown.Option("Синие"),
            ],
            border_color=C["border"],
        )

        def save(e):
            state["font_size"] = font_dropdown.value
            state["chat_wallpaper"] = wallpaper_dropdown.value
            notify("Настройки чатов обновлены")
            render()

        return subpage_screen(
            "Настройки чатов",
            "Персонализируй переписки",
            [
                panel(
                    ft.Column(
                        [
                            font_dropdown,
                            wallpaper_dropdown,
                            neon_button("Сохранить", save),
                        ],
                        spacing=12,
                    )
                ),
                setting_switch(
                    "Автозагрузка медиа",
                    "Автоматически загружать фотографии и видео",
                    "auto_download",
                ),
                setting_switch(
                    "Отчёты о прочтении",
                    "Показывать прочтение сообщений",
                    "read_receipts",
                ),
                panel(
                    ft.Column(
                        [
                            text("Другие возможности", 15,
                                 weight=ft.FontWeight.BOLD),
                            text(
                                "Закреплённые сообщения, архив, "
                                "черновики и поиск по перепискам "
                                "подключим вместе с системой чатов.",
                                12,
                                C["muted"],
                            ),
                        ],
                        spacing=7,
                    )
                ),
            ],
        )

    # -----------------------------
    # ПАПКИ ЧАТОВ
    # -----------------------------
    def create_folder(e):
        name = field("Название папки", "Например, Друзья")

        def save(ev):
            value = (name.value or "").strip()

            if not value:
                notify("Введи название папки")
                return

            state["folders"].append(value)
            page.pop_dialog()
            render()
            notify("Папка создана")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=text("Новая папка"),
                content=ft.Column(
                    [name],
                    tight=True,
                    width=300,
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

    def folders_screen():
        controls = [
            neon_button(
                "Создать папку",
                create_folder,
                ft.Icons.CREATE_NEW_FOLDER,
            )
        ]

        if not state["folders"]:
            controls.append(
                empty_state(
                    ft.Icons.FOLDER_OUTLINED,
                    "Папок пока нет",
                    "Создай папки для сортировки переписок.",
                )
            )
        else:
            for folder in state["folders"]:
                controls.append(
                    panel(
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.FOLDER,
                                    color=C["cyan"],
                                ),
                                text(
                                    folder,
                                    15,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        )
                    )
                )

        controls.append(
            text(
                "Пока папки хранятся локально. "
                "Связь с реальными чатами добавим через Firestore.",
                12,
                C["muted"],
            )
        )

        return subpage_screen(
            "Папки чатов",
            "Организуй свои переписки",
            controls,
        )

    # -----------------------------
    # О ПРИЛОЖЕНИИ
    # -----------------------------
    def about_screen():
        return subpage_screen(
            "О приложении",
            "Информация о VibeGram",
            [
                panel(
                    ft.Column(
                        [
                            ft.Container(
                                content=text(
                                    "V", 38, "white",
                                    ft.FontWeight.BOLD,
                                ),
                                width=85,
                                height=85,
                                alignment=ft.Alignment.CENTER,
                                border_radius=22,
                                gradient=ft.LinearGradient(
                                    colors=[C["purple"], C["blue"], C["cyan"]]
                                ),
                            ),
                            text("VibeGram", 24,
                                 weight=ft.FontWeight.BOLD),
                            text(
                                "Общайся. Создавай. Будь собой.",
                                13,
                                C["muted"],
                            ),
                            text("Версия 1.0", 12, C["cyan"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    )
                ),
                panel(
                    ft.Column(
                        [
                            text("О проекте", 17,
                                 weight=ft.FontWeight.BOLD),
                            text(
                                "VibeGram — приложение для общения, "
                                "личных переписок, групп и каналов.",
                                13,
                                C["muted"],
                            ),
                        ],
                        spacing=8,
                    )
                ),
            ],
        )

    # -----------------------------
    # ЧАТЫ
    # -----------------------------
    def chats_screen():
        search = field("Поиск", "Найти переписку или пользователя")

        controls = [
            heading("Чаты", "Твои личные переписки"),
            ft.Container(height=8),
            search,
            ft.Row(
                [
                    secondary_button(
                        "Папки",
                        lambda e: open_subpage("folders"),
                        ft.Icons.FOLDER_OUTLINED,
                    ),
                    secondary_button(
                        "Настройки чатов",
                        lambda e: open_subpage("chat_settings"),
                        ft.Icons.TUNE,
                    ),
                ],
                wrap=True,
            ),
        ]

        for folder in state["folders"]:
            controls.append(
                panel(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.FOLDER, color=C["cyan"]),
                            text(folder, 14),
                        ]
                    )
                )
            )

        controls.append(
            empty_state(
                ft.Icons.CHAT_BUBBLE_OUTLINE,
                "Пока нет чатов",
                "Когда появятся переписки, они будут здесь.",
            )
        )

        return ft.Column(
            controls,
            expand=True,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

    # -----------------------------
    # КОНТАКТЫ
    # -----------------------------
    def contacts_screen():
        return ft.Column(
            [
                heading(
                    "Контакты",
                    "Находи людей в VibeGram",
                ),
                ft.Container(height=12),
                panel(
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PERSON_SEARCH,
                                color=C["cyan"],
                                size=28,
                            ),
                            ft.Column(
                                [
                                    text(
                                        "Найти пользователей",
                                        15,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    text(
                                        "Поиск по username VibeGram",
                                        12,
                                        C["muted"],
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ]
                    )
                ),
                neon_button(
                    "Поиск пользователей",
                    lambda e: notify(
                        "Поиск подключим к базе пользователей Firebase"
                    ),
                    ft.Icons.SEARCH,
                ),
                empty_state(
                    ft.Icons.PEOPLE_OUTLINE,
                    "Контактов пока нет",
                    "Здесь появятся твои контакты.",
                ),
            ],
            expand=True,
            spacing=8,
        )

    # -----------------------------
    # ГРУППЫ
    # -----------------------------
    def create_group(e):
        name = field("Название группы", "Например, Друзья")
        description = field("Описание", "О чём эта группа?")

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

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=text("Новая группа"),
                content=ft.Column(
                    [name, description],
                    tight=True,
                    spacing=12,
                    width=300,
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
        items = [
            heading(
                "Группы",
                "Общайся сразу с несколькими людьми",
            ),
            neon_button(
                "Создать группу",
                create_group,
                ft.Icons.GROUP_ADD,
            ),
        ]

        if not state["groups"]:
            items.append(
                empty_state(
                    ft.Icons.GROUP_OUTLINED,
                    "Групп пока нет",
                    "Создай первую группу VibeGram.",
                )
            )
        else:
            for group in state["groups"]:
                items.append(
                    panel(
                        ft.Column(
                            [
                                text(group["name"], 16,
                                     weight=ft.FontWeight.BOLD),
                                text(
                                    group["description"] or "Группа VibeGram",
                                    12,
                                    C["muted"],
                                ),
                            ],
                            spacing=5,
                        )
                    )
                )

        return ft.Column(
            items,
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    # -----------------------------
    # КАНАЛЫ
    # -----------------------------
    def create_channel(e):
        name = field("Название канала", "Например, VibeGram News")
        description = field("Описание", "О чём канал?")

        visibility = ft.Dropdown(
            label="Тип канала",
            value="Публичный",
            options=[
                ft.dropdown.Option("Публичный"),
                ft.dropdown.Option("Приватный"),
            ],
            border_color=C["border"],
        )

        def save(ev):
            value = (name.value or "").strip()

            if not value:
                notify("Введи название канала")
                return

            state["channels"].append({
                "name": value,
                "description": (description.value or "").strip(),
                "visibility": visibility.value,
            })

            page.pop_dialog()
            render()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=text("Создать канал"),
                content=ft.Column(
                    [name, description, visibility],
                    tight=True,
                    spacing=12,
                    width=300,
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

    def channels_screen():
        items = [
            heading("Каналы", "Публикации и новости"),
            neon_button(
                "Создать канал",
                create_channel,
                ft.Icons.ADD,
            ),
        ]

        if not state["channels"]:
            items.append(
                empty_state(
                    ft.Icons.CAMPAIGN_OUTLINED,
                    "Каналов пока нет",
                    "Создай канал для своих публикаций.",
                )
            )
        else:
            for channel in state["channels"]:
                items.append(
                    panel(
                        ft.Column(
                            [
                                text(channel["name"], 16,
                                     weight=ft.FontWeight.BOLD),
                                text(
                                    channel["description"] or "Канал VibeGram",
                                    12,
                                    C["muted"],
                                ),
                                text(
                                    channel["visibility"],
                                    11,
                                    C["cyan"],
                                ),
                            ],
                            spacing=5,
                        )
                    )
                )

        return ft.Column(
            items,
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    # -----------------------------
    # НАСТРОЙКИ
    # -----------------------------
    def settings_screen():
        return ft.Column(
            [
                heading(
                    "Настройки",
                    "Управляй своим VibeGram",
                ),
                section_card(
                    ft.Icons.LANGUAGE,
                    "Язык",
                    state["language"],
                    lambda e: open_subpage("language"),
                ),
                section_card(
                    ft.Icons.CHAT_OUTLINED,
                    "Настройки чатов",
                    "Текст, обои и загрузка медиа",
                    lambda e: open_subpage("chat_settings"),
                ),
                section_card(
                    ft.Icons.FOLDER_OUTLINED,
                    "Папки чатов",
                    "Создание и управление папками",
                    lambda e: open_subpage("folders"),
                ),
                section_card(
                    ft.Icons.NOTIFICATIONS_OUTLINED,
                    "Уведомления",
                    "Звуки, вибрация и сообщения",
                    lambda e: open_subpage("notifications"),
                ),
                section_card(
                    ft.Icons.SHIELD_OUTLINED,
                    "Конфиденциальность",
                    "Видимость и безопасность",
                    lambda e: open_subpage("privacy"),
                ),
                section_card(
                    ft.Icons.PALETTE_OUTLINED,
                    "Оформление",
                    "Темы и внешний вид",
                    lambda e: open_subpage("appearance"),
                ),
                section_card(
                    ft.Icons.STAR,
                    "Vibe+",
                    "Премиальные возможности",
                    lambda e: open_subpage("plus"),
                ),
                section_card(
                    ft.Icons.INFO_OUTLINE,
                    "О приложении",
                    "Информация о VibeGram",
                    lambda e: open_subpage("about"),
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    # -----------------------------
    # ОФОРМЛЕНИЕ
    # -----------------------------
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
                    "panel2": "#1B1B32",
                    "text": "#F5F3FF",
                    "muted": "#9292AC",
                    "border": "#292944",
                })

            render()

        return subpage_screen(
            "Оформление",
            "Настрой внешний вид приложения",
            [
                panel(
                    ft.Column(
                        [
                            text("Тема приложения", 16,
                                 weight=ft.FontWeight.BOLD),
                            text(
                                "Выбирай тёмный или светлый режим",
                                12,
                                C["muted"],
                            ),
                            neon_button(
                                "Сменить тему",
                                change_theme,
                                ft.Icons.PALETTE_OUTLINED,
                            ),
                        ],
                        spacing=10,
                    )
                ),
                panel(
                    ft.Column(
                        [
                            text("Цветовая тема", 16,
                                 weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    ft.Container(
                                        width=35,
                                        height=35,
                                        bgcolor="#8B5CF6",
                                        border_radius=10,
                                    ),
                                    ft.Container(
                                        width=35,
                                        height=35,
                                        bgcolor="#3B82F6",
                                        border_radius=10,
                                    ),
                                    ft.Container(
                                        width=35,
                                        height=35,
                                        bgcolor="#22D3EE",
                                        border_radius=10,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=10,
                    )
                ),
            ],
        )

    # -----------------------------
    # НИЖНЯЯ НАВИГАЦИЯ
    # -----------------------------
    def set_tab(tab):
        state["tab"] = tab
        state["subpage"] = None
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
                            text(
                                label,
                                10,
                                C["cyan"] if active else C["muted"],
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=3,
                    ),
                    padding=ft.Padding.symmetric(
                        vertical=9,
                        horizontal=3,
                    ),
                    on_click=lambda e, t=label: set_tab(t),
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    ink=True,
                )
            )

    # -----------------------------
    # ГЛАВНЫЙ ЭКРАН
    # -----------------------------
    def render():
        page.clean()
        create_nav()

        subpage = state["subpage"]

        subpages = {
            "privacy": privacy_screen,
            "notifications": notifications_screen,
            "about": about_screen,
            "plus": plus_screen,
            "language": language_screen,
            "chat_settings": chat_settings_screen,
            "folders": folders_screen,
            "appearance": appearance_screen,
        }

        if subpage in subpages:
            screen = subpages[subpage]()
        else:
            screens = {
                "Чаты": chats_screen,
                "Контакты": contacts_screen,
                "Группы": groups_screen,
                "Каналы": channels_screen,
                "Профиль": profile_screen,
                "Настройки": settings_screen,
            }
            screen = screens.get(
                state["tab"],
                chats_screen,
            )()

        header = ft.Container(
            padding=ft.Padding.symmetric(
                horizontal=18,
                vertical=8,
            ),
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=text(
                                    "V",
                                    20,
                                    "white",
                                    ft.FontWeight.BOLD,
                                ),
                                width=38,
                                height=38,
                                alignment=ft.Alignment.CENTER,
                                border_radius=12,
                                gradient=ft.LinearGradient(
                                    colors=[C["purple"], C["blue"]],
                                ),
                            ),
                            text(
                                "VibeGram",
                                19,
                                weight=ft.FontWeight.BOLD,
                            ),
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
                        spacing=2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        body = ft.Container(
            content=screen,
            padding=ft.Padding.symmetric(
                horizontal=18,
                vertical=12,
            ),
            expand=True,
        )

        bottom = ft.Container(
            content=nav,
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            padding=ft.Padding.symmetric(
                horizontal=4,
                vertical=2,
            ),
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

    render()


ft.app(target=main)
