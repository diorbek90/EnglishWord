import flet as ft

from style import *
from database.base import *
from database.create_base import *

import threading
import random
import time
import pyttsx3
import json

from google import genai

GEMINI_API_KEY = "AIzaSyAXfe3uvZ54HPNOt53SC7ZPcOQyTCromtQ"
GEMINI_API_KEY_2 = "AIzaSyCIZdSWF-VQFzAlmlHmqIWLfvO9Yt6AmYw"
GEMINI_API_KEY_3 = "AIzaSyCkgTp5uhS1PSEyb7ZbmzU7YjoZdbkPY8w"

API_KEYS = [GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3]
current_key_index = 0

client = genai.Client(api_key=API_KEYS[current_key_index])

def rotate_client():
    global current_key_index, client
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    client = genai.Client(api_key=API_KEYS[current_key_index])
    print("🔄 Switched API key:", current_key_index)

def safe_generate(prompt, retries=3):
    global client
    for i in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()

        except Exception as ex:
            print("Retry cause:", ex)

            if "429" in str(ex) or "quota" in str(ex).lower():
                rotate_client()
                time.sleep(1)
            else:
                time.sleep(0.5)

    return None


def main(page: ft.Page):
    page.title = "Flet pages example"
    page.theme_mode = ft.ThemeMode.DARK
    page.keyboard_events = True
    init_db()

    def speak_word(word):
        def run():
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(word)
            engine.runAndWait()
            engine.stop()
        threading.Thread(target=run, daemon=True).start()

    selected_theme_id = None
    word_list = ft.ListView(expand=True, spacing=10, padding=10)
    ASK_DELETE_THEME_CONFIRM = page.client_storage.get("ask_delete_confirm") or True

    def checkbox_changed(e):
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
                    on_click=lambda e, theme_id=theme.id: page.go(f"/theme/{theme_id}")
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
            new_row = create_word_row(word, translated)
            word_list.controls.append(new_row)
            word_bs.value = ""
            translated_bs.value = ""
            close_bs_word()
            page.update()

    def delete_word_handler(e, word_id, row_ctrl):
        delete_word_by_id(word_id)
        word_list.controls.remove(row_ctrl)
        page.update()

    def close_bs_word(e=None):
        bs_for_word.open = False
        page.update()

    def create_word_row(word, translated, word_id=None):
        if word_id is None:
            word_obj = Word.select().where(Word.word == word, Word.translated == translated).get()
            word_id = word_obj.id
        row_ctrl = ft.Row([
            ft.Text(f"{word} — {translated}", size=18),
            ft.IconButton(
                icon=ft.Icons.VOLUME_UP,
                icon_color=ft.Colors.BLUE_300,
                tooltip="Speak",
                on_click=lambda e, w=word: speak_word(w)
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED_300,
                on_click=lambda e, word_id=word_id, row_ctrl=None: delete_word_handler(e, word_id, row_ctrl),
            )
        ])
        row_ctrl.controls[2].on_click = lambda e, word_id=word_id, row_ctrl=row_ctrl: delete_word_handler(e, word_id, row_ctrl)
        return row_ctrl

    def auto_translate_word(word, translated_field):
        if not word.strip():
            return

        def run():
            result = safe_generate(f'Translate the English word "{word}" into Russian. Give only one word.')
            if result:
                translated_field.value = result
                page.update()

        threading.Thread(target=run, daemon=True).start()

    def make_bottom_sheet_word():
        word_bs = ft.TextField(label="Word")
        translated_bs = ft.TextField(label="Translation")

        def on_word_submit(e):
            auto_translate_word(word_bs.value, translated_bs)
            translated_bs.focus()

        word_bs.on_submit = on_word_submit
        translated_bs.on_submit = add_word

        bs_for_word = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([ft.Text("Add Word"), word_bs, translated_bs, ft.ElevatedButton(text="Add", on_click=add_word)]),
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

    bs_for_word, word_bs, translated_bs = make_bottom_sheet_word()
    page.overlay.append(bs_for_word)

    grid_for_theme = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=150,
        spacing=20,
        run_spacing=20,
    )

    current_word = ft.Text(size=28, style=beautiful_text_style)
    result_text = ft.Text(size=20, color=ft.Colors.AMBER_300)
    answer_buttons_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    def load_new_question():
        all_words = list(Word.select())
        if len(all_words) < 4:
            result_text.value = "Need at least 4 words to play!"
            page.update()
            return

        word_obj = random.choice(all_words)
        correct_translation = word_obj.translated
        wrong_answers = [w.translated for w in all_words if w.translated != correct_translation]
        options = random.sample(wrong_answers, 3) + [correct_translation]
        random.shuffle(options)

        current_word.value = word_obj.word
        result_text.value = ""

        answer_buttons_row.controls = [
            ft.ElevatedButton(
                text=o,
                width=200,
                height=50,
                style=button_style_for_play,
                on_click=lambda e, t=o: check_answer(t, correct_translation)
            )
            for o in options
        ]
        page.update()

    def check_answer(selected, correct):
        if selected == correct:
            result_text.value = "✅ Correct!"
        else:
            result_text.value = f"❌ Wrong! Correct: {correct}"
        page.update()
        time.sleep(1.2)
        load_new_question()

    used_ai_words = set()

    def make_ai_page():
        current_word_ai = ft.Text(size=28, style=beautiful_text_style)
        ai_result_text = ft.Text(size=20, color=ft.Colors.AMBER_300)
        ai_answer_buttons_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        theme_input = ft.TextField(label="Enter a theme", width=400)

        start_btn = ft.ElevatedButton(
            text="Start AI Word Generation",
            width=250,
            height=50,
            style=button_style_for_play_ai
        )

        def load_ai_question(theme):
            ai_result_text.value = "Generating..."
            page.update()

            def run():
                avoid = ", ".join(used_ai_words) if used_ai_words else "none"

                prompt = f"""
Generate 1 English word on the theme: "{theme}".
Do NOT repeat: {avoid}

Return exactly:
WORD: <eng> 
CORRECT: <rus>
WRONG: wrong1, wrong2, wrong3, and wrong words most be on russion. All words most be begin lower letter
"""

                result = safe_generate(prompt)
                if not result:
                    ai_result_text.value = "Error. Try again"
                    page.update()
                    return

                lines = [l.strip() for l in result.splitlines() if l.strip()]

                def get(prefix):
                    for l in lines:
                        if l.upper().startswith(prefix):
                            return l.split(":", 1)[1].strip()
                    return ""

                word = get("WORD")
                correct = get("CORRECT")
                wrong_line = get("WRONG")
                wrong = [x.strip() for x in wrong_line.split(",") if x.strip()][:3]

                used_ai_words.add(word)

                options = wrong + [correct]
                random.shuffle(options)

                def update_ui():
                    current_word_ai.value = word
                    ai_result_text.value = ""

                    ai_answer_buttons_row.controls = [
                        ft.ElevatedButton(
                            text=o,
                            width=200,
                            height=50,
                            style=button_style_for_play_ai,
                            on_click=lambda e, t=o: check_ai_answer(t, correct, theme)
                        )
                        for o in options
                    ]
                    page.update()

                update_ui()

            threading.Thread(target=run, daemon=True).start()

        def check_ai_answer(selected, correct, theme):
            if selected == correct:
                ai_result_text.value = "✅ Correct!"
                speak_word(selected)
            else:
                ai_result_text.value = f"❌ Wrong! Correct: {correct}"
            page.update()

            threading.Thread(target=lambda: (time.sleep(1.5), load_ai_question(theme)), daemon=True).start()

        start_btn.on_click = lambda e: load_ai_question(theme_input.value.strip())

        return ft.View(
            route="/playWithAI",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row([theme_input, start_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=20),
                current_word_ai,
                ft.Container(height=20),
                ai_answer_buttons_row,
                ft.Container(height=20),
                ai_result_text,
                ft.Container(height=30),
                ft.ElevatedButton("Back", style=button_style_for_back, on_click=lambda e: page.go("/")),
            ],
        )

    def route_change(route):
        nonlocal selected_theme_id
        page.views.clear()

        if page.route == "/":
            grid_for_theme.controls.clear()
            for theme in Theme.select():
                grid_for_theme.controls.append(
                    ft.ElevatedButton(
                        text=theme.theme_name,
                        style=button_style_for_theme,
                        width=120,
                        height=50,
                        on_click=lambda e, t_id=theme.id: page.go(f"/theme/{t_id}")
                    )
                )

            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.Row([
                            ft.IconButton(icon=ft.Icons.ADD, icon_color=ft.Colors.GREEN_300, on_click=open_bs_theme),
                            ft.ElevatedButton("Play", style=button_style_for_play, on_click=lambda e: page.go("/play")),
                            ft.ElevatedButton("Play with AI", style=button_style_for_play_ai, on_click=lambda e: page.go("/playWithAI")),
                            ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.BLUE_300, on_click=lambda e: page.go("/settings")),
                        ]),
                        grid_for_theme
                    ]
                )
            )

        elif page.route.startswith("/theme/"):
            selected_theme_id = int(page.route.split("/")[-1])
            theme = Theme.get_by_id(selected_theme_id)

            word_list.controls.clear()
            for w in Word.select().where(Word.theme == theme):
                word_list.controls.append(create_word_row(w.word, w.translated, w.id))

            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        ft.Row([
                            ft.Text(f"Theme: {theme.theme_name}", size=22, weight=ft.FontWeight.BOLD),
                            ft.IconButton(icon=ft.Icons.ADD, icon_color=ft.Colors.GREEN_300, on_click=open_bs_word),
                            ft.ElevatedButton("Back", style=button_style_for_back, on_click=lambda e: page.go("/")),
                            ft.ElevatedButton("Delete Theme", style=button_style_for_delete, on_click=lambda e: delete_theme(selected_theme_id)),
                        ]),
                        word_list
                    ]
                )
            )

        elif page.route == "/play":
            load_new_question()
            page.views.append(
                ft.View(
                    route="/play",
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        current_word,
                        ft.Container(height=20),
                        answer_buttons_row,
                        ft.Container(height=20),
                        result_text,
                        ft.Container(height=30),
                        ft.ElevatedButton("Back", style=button_style_for_back, on_click=lambda e: page.go("/")),
                    ],
                )
            )

        elif page.route == "/settings":
            page.views.append(
                ft.View(
                    route="/settings",
                    controls=[
                        ft.Row([
                            ft.Text("Settings", size=22, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Back", style=button_style_for_back, on_click=lambda e: page.go("/")),
                        ]),
                        ft.Checkbox(
                            label="Ask before deleting theme",
                            value=ASK_DELETE_THEME_CONFIRM,
                            on_change=checkbox_changed,
                        ),
                    ],
                )
            )

        elif page.route == "/playWithAI":
            page.views.append(make_ai_page())

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
