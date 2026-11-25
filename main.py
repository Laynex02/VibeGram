
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

        "notifications": True,
        "show_online": True,
        "show_phone": False,
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
            value,
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
        page.snack_bar = ft.SnackBar(
            content=text(message)
        )
        page.snack_bar.open = True
        page.update()

    def heading(title, subtitle=None):
        controls = [
            text(title, 25, weight=ft.FontWeight.BOLD),
        ]

        if subtitle:
            controls.append(text(subtitle, 13, C["muted"]))

        return ft.Column(
            controls,
            spacing=5,
        )

    def empty_state(icon, title, subtitle):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=25,
            content=ft.Column(
                [
                    ft.Icon(
                        icon,
                        size=58,
                        color=C["purple"],
                    ),
                    text(
                        title,
                        19,
                        weight=ft.FontWeight.BOLD,
                    ),
                    text(
                        subtitle,
                        13,
                        C["muted"],
                    ),
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
                            text(
                                title,
                                15,
                                weight=ft.FontWeight.BOLD,
                            ),
                            text(
                                subtitle,
                                12,
                                C["muted"],
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
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            border_radius=18,
            padding=16,
            on_click=on_click,
            ink=True,
        )

    # -----------------------------
    # ВЫБОР ИЗОБРАЖЕНИЙ
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
        name = field(
            "Имя",
            "Твоё имя",
            state["display_name"],
        )

        username = field(
            "Username",
            "Например, vibe_user",
            state["username"],
        )

        about = field(
            "О себе",
            "Расскажи немного о себе",
            state["about"],
        )

        def save(e):
            new_username = (
                username.value or ""
            ).strip().lstrip("@")

            if not new_username:
                notify("Username не может быть пустым")
                return

            state["display_name"] = (
                name.value or ""
            ).strip()

            state["username"] = new_username

            state["about"] = (
                about.value or ""
            ).strip()

            page.pop_dialog()
            render()
            notify("Профиль обновлён")

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=text(
                    "Изменить профиль",
                    21,
                    weight=ft.FontWeight.BOLD,
                ),
                content=ft.Column(
                    [
                        name,
                        username,
                        about,
                    ],
                    tight=True,
                    spacing=12,
                    width=300,
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.TextButton(
                        "Сохранить",
                        on_click=save,
                    ),
                ],
            )
        )

    # -----------------------------
    # ПРОФИЛЬ
    # -----------------------------

    def profile_screen():

        # Аватар
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

        # Информация пользователя
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
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        # Фон профиля
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
                    colors=[
                        "#29204F",
                        "#17172E",
                        "#102B40",
                    ],
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
                ],
            ),
            height=280,
            border_radius=22,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.Border.all(1, C["border"]),
        )

        return ft.Column(
            [
                heading(
                    "Профиль",
                    "Твоя страница VibeGram",
                ),

                ft.Container(height=8),

                profile_banner,

                # Кнопки изображений
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

                ft.Container(height=5),

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
    # ПОДРАЗДЕЛЫ ПРОФИЛЯ
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
    # ПРИВАТНОСТЬ
    # -----------------------------

    def privacy_screen():
        return subpage_screen(
            "Приватность",
            "Управляй видимостью профиля",
            [
                panel(
                    ft.Column(
                        [
                            text(
                                "Показывать статус онлайн",
                                15,
                                weight=ft.FontWeight.BOLD,
                            ),

                            text(
                                "Другие пользователи смогут видеть, "
                                "когда ты в сети.",
                                12,
                                C["muted"],
                            ),

                            ft.Switch(
                                value=state["show_online"],
                                active_color=C["purple"],
                                on_change=lambda e: change_setting(
                                    "show_online",
                                    e.control.value,
                                ),
                            ),
                        ],
                        spacing=8,
                    )
                ),

                panel(
                    ft.Column(
                        [
                            text(
                                "Показывать номер телефона",
                                15,
                                weight=ft.FontWeight.BOLD,
                            ),

                            text(
                                "Разрешить другим пользователям "
                                "видеть номер телефона.",
                                12,
                                C["muted"],
                            ),

                            ft.Switch(
                                value=state["show_phone"],
                                active_color=C["purple"],
                                on_change=lambda e: change_setting(
                                    "show_phone",
                                    e.control.value,
                                ),
                            ),
                        ],
                        spacing=8,
                    )
                ),

                text(
                    "Настройки пока сохраняются только "
                    "во время текущего запуска приложения.",
                    12,
                    C["muted"],
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
                panel(
                    ft.Column(
                        [
                            text(
                                "Уведомления приложения",
                                16,
                                weight=ft.FontWeight.BOLD,
                            ),

                            text(
                                "Включить или отключить уведомления.",
                                12,
                                C["muted"],
                            ),

                            ft.Switch(
                                value=state["notifications"],
                                active_color=C["purple"],
                                on_change=lambda e: change_setting(
                                    "notifications",
                                    e.control.value,
                                ),
                            ),
                        ],
                        spacing=8,
                    )
                ),

                text(
                    "Настоящие push-уведомления подключим "
                    "при настройке Firebase.",
                    12,
                    C["muted"],
                ),
            ],
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
                                    "V",
                                    38,
                                    "white",
                                    ft.FontWeight.BOLD,
                                ),
                                width=85,
                                height=85,
                                alignment=ft.Alignment.CENTER,
                                border_radius=22,
                                gradient=ft.LinearGradient(
                                    colors=[
                                        C["purple"],
                                        C["blue"],
                                        C["cyan"],
                                    ],
                                ),
                            ),

                            text(
                                "VibeGram",
                                24,
                                weight=ft.FontWeight.BOLD,
                            ),

                            text(
                                "Общайся. Создавай. Будь собой.",
                                13,
                                C["muted"],
                            ),

                            text(
                                "Версия 1.0",
                                12,
                                C["cyan"],
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    )
                ),

                panel(
                    ft.Column(
                        [
                            text(
                                "О проекте",
                                17,
                                weight=ft.FontWeight.BOLD,
                            ),

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
    # ИЗМЕНЕНИЕ НАСТРОЕК
    # -----------------------------

    def change_setting(key, value):
        state[key] = value
        notify("Настройка изменена")

    # -----------------------------
    # ЧАТЫ
    # -----------------------------

    def chats_screen():
        return ft.Column(
            [
                heading(
                    "Чаты",
                    "Твои личные переписки",
                ),

                ft.Container(height=12),

                field(
                    "Поиск",
                    "Найти переписку или пользователя",
                ),

                empty_state(
                    ft.Icons.CHAT_BUBBLE_OUTLINE,
                    "Пока нет чатов",
                    "Когда появятся контакты, здесь будут твои переписки.",
                ),
            ],
            expand=True,
            spacing=8,
        )

    # -----------------------------
    # КОНТАКТЫ
    # -----------------------------

    def contacts_screen():
        return ft.Column(
            [
                heading(
                    "Контакты",
                    "Люди из твоей телефонной книги",
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
                        ],
                    )
                ),

                ft.Container(height=10),

                neon_button(
                    "Контакты скоро появятся",
                    lambda e: notify(
                        "Подключим контакты вместе с серверами и Firebase"
                    ),
                    ft.Icons.CONTACTS,
                ),

                empty_state(
                    ft.Icons.PEOPLE_OUTLINE,
                    "Контактов пока нет",
                    "Поиск и синхронизацию подключим позже.",
                ),
            ],
            expand=True,
            spacing=8,
        )

    # -----------------------------
    # СОЗДАНИЕ ГРУППЫ
    # -----------------------------

    def create_group(e):
        name = field(
            "Название группы",
            "Например, Друзья",
        )

        description = field(
            "Описание",
            "О чём эта группа?",
        )

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
                    [
                        name,
                        description,
                    ],
                    tight=True,
                    spacing=12,
                    width=300,
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda e: page.pop_dialog(),
                    ),

                    ft.TextButton(
                        "Создать",
                        on_click=save,
                    ),
                ],
            )
        )

    # -----------------------------
    # ГРУППЫ
    # -----------------------------

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
                                text(
                                    group["name"],
                                    16,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                text(
                                    group["description"] or "Группа VibeGram",
                                    12,
                                    C["muted"],
                                ),

                                text(
                                    "Участники и сообщения подключим к Firebase",
                                    11,
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
    # СОЗДАНИЕ КАНАЛА
    # -----------------------------

    def create_channel(e):
        name = field(
            "Название канала",
            "Например, VibeGram News",
        )

        description = field(
            "Описание",
            "О чём канал?",
        )

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
                    [
                        name,
                        description,
                        visibility,
                    ],
                    tight=True,
                    spacing=12,
                    width=300,
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda e: page.pop_dialog(),
                    ),

                    ft.TextButton(
                        "Создать",
                        on_click=save,
                    ),
                ],
            )
        )

    # -----------------------------
    # КАНАЛЫ
    # -----------------------------

    def channels_screen():
        items = [
            heading(
                "Каналы",
                "Публикации и новости",
            ),

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
                                text(
                                    channel["name"],
                                    16,
                                    weight=ft.FontWeight.BOLD,
                                ),

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

                                text(
                                    "Публикации и подписчики подключим к Firebase",
                                    11,
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
    # НАСТРОЙКИ ОФОРМЛЕНИЯ
    # -----------------------------

    def settings_screen():

        def change_theme(e):
            if state["theme"] == "dark":
                state["theme"] = "light"

                page.theme_mode = ft.ThemeMode.LIGHT
                page.bgcolor = "#F4F2FF"

                C["bg"] = "#F4F2FF"
                C["panel"] = "#FFFFFF"
                C["panel2"] = "#EEEEF8"
                C["text"] = "#17152A"
                C["muted"] = "#77738D"
                C["border"] = "#DDD9EA"

            else:
                state["theme"] = "dark"

                page.theme_mode = ft.ThemeMode.DARK
                page.bgcolor = "#090914"

                C["bg"] = "#090914"
                C["panel"] = "#141426"
                C["panel2"] = "#1B1B32"
                C["text"] = "#F5F3FF"
                C["muted"] = "#9292AC"
                C["border"] = "#292944"

            render()

        return ft.Column(
            [
                heading(
                    "Оформление",
                    "Настрой VibeGram под себя",
                ),

                panel(
                    ft.Column(
                        [
                            text(
                                "Тема приложения",
                                16,
                                weight=ft.FontWeight.BOLD,
                            ),

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
                            text(
                                "Цветовая тема",
                                16,
                                weight=ft.FontWeight.BOLD,
                            ),

                            text(
                                "Неоновый фиолетово-синий стиль.",
                                12,
                                C["muted"],
                            ),

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

                text(
                    "Настраиваемые палитры и фоны чатов "
                    "добавим следующим этапом.",
                    12,
                    C["muted"],
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
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

        if subpage == "privacy":
            screen = privacy_screen()

        elif subpage == "notifications":
            screen = notifications_screen()

        elif subpage == "about":
            screen = about_screen()

        elif state["tab"] == "Чаты":
            screen = chats_screen()

        elif state["tab"] == "Контакты":
            screen = contacts_screen()

        elif state["tab"] == "Группы":
            screen = groups_screen()

        elif state["tab"] == "Каналы":
            screen = channels_screen()

        elif state["tab"] == "Профиль":
            screen = profile_screen()

        else:
            screen = settings_screen()

        # Верхняя панель
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
                                    colors=[
                                        C["purple"],
                                        C["blue"],
                                    ],
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
                                ft.Icons.PALETTE_OUTLINED,
                                icon_color=C["cyan"],
                                tooltip="Оформление",
                                on_click=lambda e: set_tab("Настройки"),
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

        # Основная область
        body = ft.Container(
            content=screen,
            padding=ft.Padding.symmetric(
                horizontal=18,
                vertical=12,
            ),
            expand=True,
        )

        # Нижняя навигация
        bottom = ft.Container(
            content=nav,
            bgcolor=C["panel"],
            border=ft.Border.all(1, C["border"]),
            padding=ft.Padding.symmetric(
                horizontal=4,
                vertical=2,
            ),
        )

        # SafeArea защищает от статус-бара и системной панели Android
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
