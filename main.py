from flet_firebase_auth import FirebaseAuth
import flet as ft

def main(page: ft.Page):
    firebase_auth = FirebaseAuth()
    page.services.append(firebase_auth)
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
        "theme": "dark",
        "username": "",
        "display_name": "",
        "about": "",
        "groups": [],
        "channels": [],
        "messages": {},
        "current_chat": None,
    }

    content = ft.Column(expand=True, spacing=0)
    nav = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        spacing=0,
    )

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
            border=ft.border.all(1, C["border"]),
            border_radius=18,
            padding=padding,
        )

    def neon_button(label, on_click, icon=None):
        return ft.ElevatedButton(
            text=label,
            icon=icon,
            on_click=on_click,
            bgcolor=C["purple"],
            color="white",
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
            ),
        )

    def field(label, hint="", password=False):
        return ft.TextField(
            label=label,
            hint_text=hint,
            password=password,
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
        items = [
            text(title, 25, weight=ft.FontWeight.BOLD),
        ]
        if subtitle:
            items.append(text(subtitle, 13, C["muted"]))
        return ft.Column(items, spacing=5)

    def section_card(icon, title, subtitle):
        return panel(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=C["cyan"], size=25),
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
            )
        )

    def show_login():
        page.clean()

        logo = ft.Container(
            content=ft.Text(
                "V",
                size=52,
                weight=ft.FontWeight.BOLD,
                color="white",
            ),
            width=100,
            height=100,
            alignment=ft.Alignment.CENTER,
            border_radius=28,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[C["purple"], C["blue"], C["cyan"]],
            ),
        )

        email = field("Email", "Твой Google-аккаунт")

        page.add(
            ft.Container(
                expand=True,
                bgcolor=C["bg"],
                alignment=ft.Alignment.CENTER,
                padding=25,
                content=ft.Column(
                    [
                        logo,
                        text("VibeGram", 32, weight=ft.FontWeight.BOLD),
                        text(
                            "Общайся. Создавай. Будь собой.",
                            14,
                            C["muted"],
                        ),
                        ft.Container(height=25),
                        panel(
                            ft.Column(
                                [
                                    text("Добро пожаловать!", 21,
                                         weight=ft.FontWeight.BOLD),
                                    text(
                                        "Войди в свой аккаунт VibeGram",
                                        13,
                                        C["muted"],
                                    ),
                                    email,
                                    neon_button(
                                        "Продолжить через Google",
                                        lambda e: notify(
                                            "Google-вход подключим через Firebase"
                                        ),
                                        ft.Icons.LOGIN,
                                    ),
                                    text(
                                        "Авторизация пока настраивается. "
                                        "Аккаунты не создаются до подключения Firebase.",
                                        11,
                                        C["muted"],
                                    ),
                                ],
                                spacing=15,
                            )
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
            )
        )

    def set_tab(tab):
        state["tab"] = tab
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
                    padding=ft.Padding.symmetric(vertical=10, horizontal=5),
                    on_click=lambda e, t=label: set_tab(t),
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                )
            )

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

    def chats_screen():
        return ft.Column(
            [
                heading("Чаты", "Твои личные переписки"),
                ft.Container(height=12),
                field("Поиск", "Найти переписку или пользователя"),
                ft.Container(height=10),
                empty_state(
                    ft.Icons.CHAT_BUBBLE_OUTLINE,
                    "Пока нет чатов",
                    "Когда появятся контакты, здесь будут твои переписки.",
                ),
            ],
            expand=True,
            spacing=8,
        )

    def contacts_screen():
        return ft.Column(
            [
                heading("Контакты", "Люди из твоей телефонной книги"),
                ft.Container(height=12),
                section_card(
                    ft.Icons.PERSON_SEARCH,
                    "Найти пользователей",
                    "Поиск по username VibeGram",
                ),
                ft.Container(height=10),
                neon_button(
                    "Разрешить доступ к контактам",
                    lambda e: notify(
                        "Доступ к телефонной книге подключим через Android"
                    ),
                    ft.Icons.CONTACTS,
                ),
                ft.Container(height=12),
                empty_state(
                    ft.Icons.PEOPLE_OUTLINE,
                    "Контактов пока нет",
                    "Сначала подключим аккаунты и безопасный поиск контактов.",
                ),
            ],
            expand=True,
            spacing=8,
        )

    def create_group(e):
        name = field("Название группы", "Например, Друзья")
        description = field("Описание", "О чём эта группа?")

        def save(ev):
            value = name.value.strip()
            if not value:
                notify("Введи название группы")
                return
            state["groups"].append({
                "name": value,
                "description": description.value.strip(),
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
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda ev: page.pop_dialog(),
                    ),
                    ft.TextButton("Создать", on_click=save),
                ],
            )
        )

    def groups_screen():
        items = [
            heading("Группы", "Общайся сразу с несколькими людьми"),
            ft.Container(height=10),
            neon_button(
                "Создать группу",
                create_group,
                ft.Icons.GROUP_ADD,
            ),
            ft.Container(height=10),
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

        return ft.Column(items, expand=True, spacing=8)

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
            value = name.value.strip()
            if not value:
                notify("Введи название канала")
                return
            state["channels"].append({
                "name": value,
                "description": description.value.strip(),
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
                ),
                actions=[
                    ft.TextButton(
                        "Отмена",
                        on_click=lambda ev: page.pop_dialog(),
                    ),
                    ft.TextButton("Создать", on_click=save),
                ],
            )
        )

    def channels_screen():
        items = [
            heading("Каналы", "Публикации и новости"),
            ft.Container(height=10),
            neon_button(
                "Создать канал",
                create_channel,
                ft.Icons.ADD,
            ),
            ft.Container(height=10),
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

        return ft.Column(items, expand=True, spacing=8)

    def profile_screen():
        name = field("Имя", state["display_name"])
        username = field("Username", state["username"])
        about = field("О себе", state["about"])

        def save_profile(e):
            state["display_name"] = name.value.strip()
            state["username"] = username.value.strip().lstrip("@")
            state["about"] = about.value.strip()
            notify("Изменения сохранены на этом устройстве")
            render()

        return ft.Column(
            [
                heading("Профиль", "Твоя страница VibeGram"),
                ft.Container(height=12),
                panel(
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.PERSON,
                                    size=45,
                                    color=C["cyan"],
                                ),
                                width=90,
                                height=90,
                                bgcolor="#25213F",
                                border_radius=45,
                                alignment=ft.Alignment.CENTER,
                            ),
                            text(
                                state["display_name"] or "Твоё имя",
                                20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            text(
                                "@" + state["username"]
                                if state["username"]
                                else "@username",
                                13,
                                C["muted"],
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    )
                ),
                name,
                username,
                about,
                neon_button("Сохранить профиль", save_profile),
                section_card(
                    ft.Icons.SHIELD_OUTLINED,
                    "Приватность",
                    "Настройки безопасности и видимости",
                ),
                section_card(
                    ft.Icons.NOTIFICATIONS_OUTLINED,
                    "Уведомления",
                    "Настройка уведомлений",
                ),
                section_card(
                    ft.Icons.INFO_OUTLINE,
                    "О приложении",
                    "VibeGram — общайся без границ",
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    def settings_screen():
        def change_theme(e):
            if state["theme"] == "dark":
                state["theme"] = "light"
                page.theme_mode = ft.ThemeMode.LIGHT
                page.bgcolor = "#F4F2FF"
                C["bg"] = "#F4F2FF"
                C["panel"] = "#FFFFFF"
                C["text"] = "#17152A"
                C["muted"] = "#77738D"
            else:
                state["theme"] = "dark"
                page.theme_mode = ft.ThemeMode.DARK
                page.bgcolor = "#090914"
                C["bg"] = "#090914"
                C["panel"] = "#141426"
                C["text"] = "#F5F3FF"
                C["muted"] = "#9292AC"
            render()

        return ft.Column(
            [
                heading("Оформление", "Настрой VibeGram под себя"),
                ft.Container(height=12),
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
                            text(
                                "Сейчас используется неоновый фиолетово-синий стиль.",
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
                    "Настраиваемые палитры и фоны чатов добавим следующим этапом.",
                    12,
                    C["muted"],
                ),
            ],
            spacing=12,
        )

    def render():
        page.clean()
        create_nav()

        if state["tab"] == "Чаты":
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

        header = ft.Container(
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
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
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        body = ft.Container(
            content=screen,
            padding=18,
            expand=True,
        )

        bottom = ft.Container(
            content=nav,
            bgcolor=C["panel"],
            border=ft.border.all(1, C["border"]),
            padding=ft.Padding.symmetric(horizontal=5),
        )

        page.add(
            ft.Column(
                [
                    header,
                    body,
                    bottom,
                ],
                expand=True,
                spacing=0,
            )
        )
        page.update()

    render()


ft.app(target=main)
