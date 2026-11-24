
import flet as ft


# VibeGram — neon messenger UI prototype
# Compatible with modern Flet API (0.86+)

BG = "#080914"
SURFACE = "#111426"
SURFACE_LIGHT = "#191E35"
PURPLE = "#9B5CFF"
BLUE = "#397BFF"
CYAN = "#38D9FF"
WHITE = "#F5F6FF"
MUTED = "#9299B5"
GREEN = "#42D9A0"


CHATS = [
    {
        "name": "Alex",
        "message": "Давай созвонимся вечером?",
        "time": "12:40",
        "unread": 2,
        "color": "#8B5CF6",
        "online": True,
    },
    {
        "name": "Maria",
        "message": "Отправила тебе фото ✨",
        "time": "11:25",
        "unread": 0,
        "color": "#EC4899",
        "online": True,
    },
    {
        "name": "VibeGram Team",
        "message": "Добро пожаловать в VibeGram!",
        "time": "Вчера",
        "unread": 1,
        "color": "#397BFF",
        "online": False,
    },
    {
        "name": "Daniel",
        "message": "Отлично, договорились 👍",
        "time": "Вчера",
        "unread": 0,
        "color": "#14B8A6",
        "online": False,
    },
]


def main(page: ft.Page):
    page.title = "VibeGram"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.window.min_width = 320
    page.window.min_height = 550

    current_chat = None
    current_tab = 0
    messages = {}

    def neon_text(value, size=20, color=WHITE, weight=ft.FontWeight.NORMAL):
        return ft.Text(
            value,
            size=size,
            color=color,
            weight=weight,
        )

    def avatar(name, color, size=52, online=False):
        letter = name[0].upper() if name else "?"

        avatar_content = ft.Container(
            width=size,
            height=size,
            border_radius=size / 2,
            bgcolor=color,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(
                letter,
                size=size * 0.42,
                color=WHITE,
                weight=ft.FontWeight.BOLD,
            ),
        )

        if not online:
            return avatar_content

        return ft.Stack(
            width=size,
            height=size,
            controls=[
                avatar_content,
                ft.Container(
                    width=13,
                    height=13,
                    right=0,
                    bottom=0,
                    bgcolor=GREEN,
                    border_radius=10,
                    border=ft.Border.all(2, BG),
                ),
            ],
        )

    def header():
        return ft.Container(
            padding=ft.Padding.only(
                left=20, right=20, top=18, bottom=12
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Row(
                                spacing=5,
                                controls=[
                                    neon_text("Vibe", 27, WHITE, ft.FontWeight.BOLD),
                                    neon_text("Gram", 27, CYAN, ft.FontWeight.BOLD),
                                ],
                            ),
                            neon_text("Общайся без границ", 12, MUTED),
                        ],
                    ),
                    ft.Container(
                        width=43,
                        height=43,
                        border_radius=15,
                        bgcolor=SURFACE_LIGHT,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            ft.Icons.ADD,
                            color=CYAN,
                            size=25,
                        ),
                        on_click=lambda e: show_notice(
                            "Создание нового чата появится позже"
                        ),
                    ),
                ],
            ),
        )

    def show_notice(message):
        page.open(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=SURFACE_LIGHT,
            )
        )

    def chat_tile(chat):
        def open_chat(e):
            open_conversation(chat)

        unread_controls = []
        if chat["unread"] > 0:
            unread_controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                    border_radius=20,
                    bgcolor=PURPLE,
                    content=ft.Text(
                        str(chat["unread"]),
                        size=11,
                        color=WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            )

        return ft.Container(
            padding=12,
            border_radius=18,
            bgcolor=SURFACE,
            on_click=open_chat,
            content=ft.Row(
                spacing=12,
                controls=[
                    avatar(
                        chat["name"],
                        chat["color"],
                        52,
                        chat["online"],
                    ),
                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=[
                            neon_text(
                                chat["name"],
                                15,
                                WHITE,
                                ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                chat["message"],
                                size=12,
                                color=MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=9,
                        controls=[
                            ft.Text(
                                chat["time"],
                                size=10,
                                color=MUTED,
                            ),
                            *unread_controls,
                        ],
                    ),
                ],
            ),
        )

    def home_content():
        search_field = ft.TextField(
            hint_text="Поиск чатов...",
            prefix_icon=ft.Icons.SEARCH,
            filled=True,
            bgcolor=SURFACE,
            border=ft.InputBorder.NONE,
            border_radius=16,
            color=WHITE,
            hint_style=ft.TextStyle(color=MUTED),
            on_change=lambda e: filter_chats(e.control.value),
        )

        chat_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=ft.Padding.only(left=16, right=16, bottom=12),
        )

        def fill_chats(items):
            chat_list.controls.clear()
            for item in items:
                chat_list.controls.append(chat_tile(item))
            page.update()

        def filter_chats(value):
            query = value.lower().strip()
            filtered = [
                chat for chat in CHATS
                if query in chat["name"].lower()
                or query in chat["message"].lower()
            ]
            fill_chats(filtered)

        fill_chats(CHATS)

        return ft.Column(
            expand=True,
            spacing=12,
            controls=[
                header(),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16),
                    content=search_field,
                ),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=20),
                    content=neon_text("Сообщения", 19, WHITE, ft.FontWeight.BOLD),
                ),
                chat_list,
            ],
        )

    def open_conversation(chat):
        nonlocal current_chat
        current_chat = chat

        if chat["name"] not in messages:
            messages[chat["name"]] = [
                ("Привет! Как дела?", False),
                ("Всё отлично! А у тебя?", True),
            ]

        render_conversation()

    def render_conversation():
        page.clean()

        chat = current_chat
        if chat is None:
            render_home()
            return

        message_list = ft.ListView(
            expand=True,
            spacing=12,
            padding=16,
            auto_scroll=True,
        )

        def add_message(text, mine):
            bubble_color = "#29204A" if mine else SURFACE_LIGHT

            message_list.controls.append(
                ft.Row(
                    alignment=(
                        ft.MainAxisAlignment.END
                        if mine
                        else ft.MainAxisAlignment.START
                    ),
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=16,
                            bgcolor=bubble_color,
                            border=ft.Border.all(
                                1,
                                "#7548C9" if mine else "#252B46",
                            ),
                            width=None,
                            content=ft.Text(
                                text,
                                color=WHITE,
                                size=14,
                            ),
                        ),
                    ],
                )
            )

        for text, mine in messages[chat["name"]]:
            add_message(text, mine)

        message_input = ft.TextField(
            hint_text="Написать сообщение...",
            expand=True,
            filled=True,
            bgcolor=SURFACE_LIGHT,
            border=ft.InputBorder.NONE,
            border_radius=18,
            color=WHITE,
            hint_style=ft.TextStyle(color=MUTED),
            text_size=14,
            on_submit=lambda e: send_message(),
        )

        def send_message():
            value = message_input.value.strip()
            if not value:
                return

            messages[chat["name"]].append((value, True))
            message_input.value = ""
            render_conversation()

        page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        ft.Container(
                            padding=12,
                            bgcolor=SURFACE,
                            content=ft.Row(
                                spacing=12,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        icon_color=CYAN,
                                        on_click=lambda e: render_home(),
                                    ),
                                    avatar(
                                        chat["name"],
                                        chat["color"],
                                        42,
                                        chat["online"],
                                    ),
                                    ft.Column(
                                        expand=True,
                                        spacing=2,
                                        controls=[
                                            neon_text(
                                                chat["name"],
                                                15,
                                                WHITE,
                                                ft.FontWeight.BOLD,
                                            ),
                                            neon_text(
                                                "В сети" if chat["online"] else "Не в сети",
                                                11,
                                                GREEN if chat["online"] else MUTED,
                                            ),
                                        ],
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CALL_OUTLINED,
                                        icon_color=CYAN,
                                        on_click=lambda e: show_notice(
                                            "Звонки появятся позже"
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.MORE_VERT,
                                        icon_color=WHITE,
                                        on_click=lambda e: show_notice(
                                            "Дополнительные функции появятся позже"
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            content=message_list,
                        ),
                        ft.Container(
                            padding=12,
                            bgcolor=SURFACE,
                            content=ft.Row(
                                spacing=8,
                                controls=[
                                    message_input,
                                    ft.Container(
                                        width=46,
                                        height=46,
                                        border_radius=16,
                                        gradient=ft.LinearGradient(
                                            begin=ft.Alignment.CENTER_LEFT,
                                            end=ft.Alignment.CENTER_RIGHT,
                                            colors=[PURPLE, BLUE],
                                        ),
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(
                                            ft.Icons.SEND,
                                            color=WHITE,
                                        ),
                                        on_click=lambda e: send_message(),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            )
        )
        page.update()

    def render_home():
        nonlocal current_chat
        current_chat = None
        page.clean()

        def change_tab(e):
            nonlocal current_tab
            current_tab = e.control.selected_index

            if current_tab == 0:
                render_home()
            elif current_tab == 1:
                show_placeholder("Контакты")
            elif current_tab == 2:
                show_placeholder("Профиль")

        page.navigation_bar = ft.NavigationBar(
            selected_index=current_tab,
            bgcolor=SURFACE,
            indicator_color="#33245D",
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                    selected_icon=ft.Icons.CHAT_BUBBLE,
                    label="Чаты",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.PEOPLE_OUTLINE,
                    selected_icon=ft.Icons.PEOPLE,
                    label="Контакты",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.PERSON_OUTLINE,
                    selected_icon=ft.Icons.PERSON,
                    label="Профиль",
                ),
            ],
            on_change=change_tab,
        )

        page.add(
            ft.SafeArea(
                expand=True,
                content=home_content(),
            )
        )
        page.update()

    def show_placeholder(title):
        page.clean()
        page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.AUTO_AWESOME,
                            size=55,
                            color=PURPLE,
                        ),
                        neon_text(title, 24, WHITE, ft.FontWeight.BOLD),
                        neon_text(
                            "Этот раздел скоро появится",
                            14,
                            MUTED,
                        ),
                        ft.Button(
                            content="Вернуться к чатам",
                            on_click=lambda e: (
                                set_home_tab()
                            ),
                        ),
                    ],
                ),
            )
        )
        page.update()

    def set_home_tab():
        nonlocal current_tab
        current_tab = 0
        render_home()

    render_home()


if __name__ == "__main__":
    ft.run(main)
