import flet as ft
from style import *
from database.base import *
from database.create_base import *

def main(page: ft.Page):
    page.title = "Flet pages example"
    page.theme_mode = ft.ThemeMode.DARK
    page.keyboard_events = True
    init_db()

    selected_theme_id = None
    word_list = ft.Column()

    ASK_DELETE_THEME_CONFIRM = page.client_storage.get("ask_delete_confirm") or True

    def chackbox_changed(e):
        nonlocal ASK_DELETE_THEME_CONFIRM
        ASK_DELETE_THEME_CONFIRM = e.control.value
        page.client_storage.set("ask_delete_confirm", ASK_DELETE_THEME_CONFIRM)

    def close_bs_theme(e=None):
        theme_bs.error_text = None
        bs_for_theme.open = False
        page.update()

    def add_theme(e=None):
        text = theme_bs.value.strip()
        if text and not is_there_theme(text):
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
        else:
            theme_bs.error_text = "Theme already exists!"
            page.update()

    def delete_theme(theme_id):
        def confirm_delete(e):
            delete_theme_by_id(theme_id)
            page.close(delete_dialog)
            page.go("/")
            page.update()

        delete_dialog = ft.AlertDialog(
            title=ft.Text("Delete Theme"),
            content=ft.Text("Are you sure you want to delete this theme and all its words?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.close(delete_dialog)),
                ft.TextButton("Delete", on_click=confirm_delete),
            ],
        )

        if ASK_DELETE_THEME_CONFIRM:
            page.open(delete_dialog)
        else:
            delete_theme_by_id(theme_id)
            page.go("/")

        page.update()

    def open_bs_theme(e=None):
        bs_for_theme.open = True
        theme_bs.focus()
        page.update()

    theme_bs = ft.TextField(on_submit=add_theme)

    bs_for_theme = ft.BottomSheet(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Add Theme"),
                theme_bs,
                ft.ElevatedButton(text="Add", on_click=add_theme)
            ]),
            padding=20,
        )
    )

    page.overlay.append(bs_for_theme)

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

    def close_bs_word(e=None):
        bs_for_word.open = False
        page.update()

    def make_bottom_sheet_word():
        word_bs = ft.TextField(label="Word")
        translated_bs = ft.TextField(label="Translation")
        add_btn = ft.ElevatedButton(text="Add", on_click=add_word)
        word_bs.on_submit = lambda e: translated_bs.focus()
        translated_bs.on_submit = add_word
        bs_for_word = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Add Word"),
                    word_bs,
                    translated_bs,
                    add_btn
                ]),
                padding=30
            )
        )
        return bs_for_word, word_bs, translated_bs

    def open_bs_word(e=None):
        nonlocal bs_for_word, word_bs, translated_bs
        bs_for_word, word_bs, translated_bs = make_bottom_sheet_word()
        page.overlay.append(bs_for_word)
        bs_for_word.open = True
        page.update()
        word_bs.focus()
        page.update()

    bs_for_word, word_bs, translated_bs = make_bottom_sheet_word()
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
                    ),
                )

            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                icon_color=ft.Colors.GREEN_300,
                                icon_size=40,
                                on_click=open_bs_theme
                            ),
                            ft.ElevatedButton(
                                text="Play",
                                style=button_style_for_play,
                                width=120,
                                height=50,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.SETTINGS,
                                icon_color=ft.Colors.BLUE_300,
                                icon_size=40,
                                on_click=lambda e: page.go("/settings")
                            )
                        ]),
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
                            ft.Text(f"Theme: {theme.theme_name}", size=24, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                icon_color=ft.Colors.GREEN_300,
                                icon_size=40,
                                on_click=open_bs_word
                            ),
                            ft.ElevatedButton("Back", style=button_style_for_back,
                                              on_click=lambda e: page.go("/")),
                            ft.ElevatedButton("Delete Theme", style=button_style_for_delete,
                                              on_click=lambda e: delete_theme(theme_id)),
                        ]),
                        word_list,
                    ],
                )
            )

        elif page.route == "/settings":
            page.views.append(
                ft.View(
                    route="/settings",
                    controls=[
                        ft.Row([
                            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Back", style=button_style_for_back,
                                              on_click=lambda e: page.go("/")),
                        ]),
                        ft.Checkbox(
                                label="Ask before deleting theme",
                                value=ASK_DELETE_THEME_CONFIRM,
                                on_change=chackbox_changed,
                            ),
                    ],
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go(page.route)

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            if page.route == "/" and not bs_for_theme.open:
                open_bs_theme()
            elif page.route.startswith("/theme/") and not bs_for_word.open:
                open_bs_word()

    page.on_keyboard_event = on_keyboard


if __name__ == "__main__":
    ft.app(main)