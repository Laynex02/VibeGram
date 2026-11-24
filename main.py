import flet as ft

BG = "#080B18"
PANEL = "#11172A"
PURPLE = "#8B5CF6"
CYAN = "#22D3EE"
TEXT = "#F4F7FF"
MUTED = "#8D98B5"

def main(page: ft.Page):
    page.title = "VibeGram"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.window_width = 390
    page.window_height = 820

    messages = [
        ("Алекс", "Привет! Как дела?", "12:41", "A"),
        ("Мария", "Посмотри, что я отправила ✨", "11:58", "М"),
        ("Команда VibeGram", "Добро пожаловать!", "Вчера", "V"),
    ]

    def open_chat(name):
        page.controls.clear()
        chat_messages = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    content=ft.Text("Привет! Это тестовый чат VibeGram 👋", color=TEXT),
                    bgcolor=PANEL, padding=12, border_radius=14,
                    alignment=ft.alignment.center_left,
                )
            ],
        )
        entry = ft.TextField(
            hint_text="Написать сообщение...",
            expand=True,
            border_color=PURPLE,
            focused_border_color=CYAN,
            bgcolor=PANEL,
            text_size=14,
        )

        def send_message(e):
            value = entry.value.strip()
            if value:
                chat_messages.controls.append(
                    ft.Container(
                        content=ft.Text(value, color=TEXT),
                        bgcolor="#35245F", padding=12, border_radius=14,
                        alignment=ft.alignment.center_right,
                    )
                )
                entry.value = ""
                page.update()

        page.add(
            ft.Container(
                padding=16,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.Row([
                            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_home()),
                            ft.Text(name, size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                        ]),
                        ft.Divider(color="#252D46"),
                        chat_messages,
                        ft.Row([entry, ft.IconButton(ft.Icons.SEND_ROUNDED, icon_color=CYAN, on_click=send_message)]),
                    ],
                ),
            )
        )
        page.update()

    def show_home():
        page.controls.clear()
        chat_list = ft.Column(
            spacing=8,
            controls=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.CircleAvatar(content=ft.Text(initial), bgcolor="#35245F", color=CYAN),
                            ft.Column(
                                [
                                    ft.Text(name, color=TEXT, weight=ft.FontWeight.BOLD),
                                    ft.Text(message, color=MUTED, size=12),
                                ],
                                expand=True,
                                spacing=3,
                            ),
                            ft.Text(time, color=MUTED, size=11),
                        ],
                    ),
                    bgcolor=PANEL,
                    padding=12,
                    border_radius=16,
                    on_click=lambda e, n=name: open_chat(n),
                )
                for name, message, time, initial in messages
            ],
        )

        page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            [
                                ft.Container(
                                    width=42, height=42, border_radius=14,
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.top_left,
                                        end=ft.alignment.bottom_right,
                                        colors=[PURPLE, CYAN],
                                    ),
                                    content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF_ROUNDED, color="#080B18", size=24),
                                    alignment=ft.alignment.center,
                                ),
                                ft.Text("VibeGram", size=25, weight=ft.FontWeight.BOLD, color=TEXT),
                                ft.Container(expand=True),
                                ft.IconButton(ft.Icons.PERSON_OUTLINE, icon_color=CYAN),
                            ],
                        ),
                        ft.Text("Твои разговоры", size=22, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text("Общайся без границ", color=MUTED, size=13),
                        ft.TextField(
                            hint_text="Поиск чатов...",
                            prefix_icon=ft.Icons.SEARCH,
                            border_color="#29324D",
                            focused_border_color=PURPLE,
                            bgcolor=PANEL,
                        ),
                        ft.Container(height=8),
                        chat_list,
                        ft.Container(expand=True),
                        ft.Row(
                            [
                                ft.Column([ft.Icon(ft.Icons.CHAT_BUBBLE, color=CYAN), ft.Text("Чаты", color=CYAN, size=11)], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Container(expand=True),
                                ft.Column([ft.Icon(ft.Icons.CONTACTS_OUTLINED, color=MUTED), ft.Text("Контакты", color=MUTED, size=11)], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Container(expand=True),
                                ft.Column([ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, color=MUTED), ft.Text("Профиль", color=MUTED, size=11)], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ],
                        ),
                    ],
                ),
            )
        )
        page.update()

    show_home()

ft.app(target=main)
