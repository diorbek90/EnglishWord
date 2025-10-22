import flet as ft
from style import *
from database.base import *
from database.create_base import create_theme, create_word, init_db

def main(page: ft.Page):
    page.title = "Flet pages example"
    page.theme_mode = ft.ThemeMode.DARK
    page.keyboard_events = True
    init_db()

    selected_theme_id = None
    word_list = ft.Column()

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            if page.route == "/":
                open_bs_theme()
            elif page.route.startswith("/theme/"):
                open_bs_word()

    page.on_keyboard_event = on_keyboard

    def close_bs_theme(e=None):
        bs_for_theme.open = False
        page.update()

    def add_theme(e=None):
        text = theme_bs.value.strip()
        if text:
            create_theme(theme=text)
            theme = Theme.get(Theme.theme_name == text)
            grid_for_theme.controls.append(
                ft.ElevatedButton(
                    text=theme.theme_name,
                    style=button_style_for_theme,
                    width=120,
                    height=50,
                    on_click=lambda e: page.go(f"/theme/{theme.id}")
                )
            )
            theme_bs.value = ""
            close_bs_theme()
            page.update()

    def open_bs_theme(e=None):
        bs_for_theme.open = True
        theme_bs.focus()
        page.update()

    theme_bs = ft.TextField(on_submit=add_theme)

    bs_for_theme = ft.BottomSheet(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Добавить тему"),
                theme_bs,
                ft.ElevatedButton(text="Добавить", on_click=add_theme)
            ]),
            padding=20,
        )
    )

    page.overlay.append(bs_for_theme)

    def open_bs_word(e=None):
        bs_for_word.open = True
        word_bs.focus()
        page.update()
        

    def close_bs_word(e=None):
        bs_for_word.open = False
        word_bs.focus()
        page.update()

    def add_word(e=None):
        word = word_bs.value.strip()
        translated = translated_bs.value.strip()
        if word and translated and selected_theme_id:
            create_word(word=word, translated=translated, id=selected_theme_id)
            word_list.controls.append(ft.Text(f"{word} — {translated}", size=18))
            word_bs.value = ""
            translated_bs.value = ""
            close_bs_word()
            page.update()

    word_bs = ft.TextField(on_submit=lambda e: translated_bs.focus())
    translated_bs = ft.TextField(on_submit=add_word)

    bs_for_word = ft.BottomSheet(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Добавить слово"),
                word_bs,
                translated_bs,
                ft.ElevatedButton(text="Добавить", on_click=add_word)
            ]),
            padding=30
        )
    )

    page.overlay.append(bs_for_word)

    grid_for_theme = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=150,
        spacing=10,
        run_spacing=10,
    )

    def route_change(route):
        nonlocal selected_theme_id
        page.views.clear()

        if page.route == "/":
            grid_for_theme.controls.clear()
            themes = Theme.select()
            for theme in themes:
                grid_for_theme.controls.append(
                    ft.ElevatedButton(
                        text=theme.theme_name,
                        style=button_style_for_theme,
                        width=120,
                        height=50,
                        on_click=lambda e, theme_id=theme.id: page.go(f"/theme/{theme_id}")
                    )
                )

            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_color=ft.Colors.GREEN_300,
                            icon_size=40,
                            on_click=open_bs_theme
                        ),
                        grid_for_theme
                    ],
                )
            )

        elif page.route.startswith("/theme/"):
            theme_id = int(page.route.split("/")[-1])
            selected_theme_id = theme_id
            theme = Theme.get_by_id(theme_id)
            words = Word.select().where(Word.theme == theme)

            word_list.controls.clear()
            for word in words:
                word_list.controls.append(
                    ft.Text(f"{word.word} — {word.translated}", size=18)
                )

            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        ft.Row([
                            ft.Text(f"Тема: {theme.theme_name}", size=24, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                icon_color=ft.Colors.GREEN_300,
                                icon_size=40,
                                on_click=open_bs_word
                            )
                        ]),
                        word_list,
                        ft.ElevatedButton("Назад", on_click=lambda e: page.go("/")),
                    ],
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go(page.route)

ft.app(main)
