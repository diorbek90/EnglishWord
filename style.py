import flet as ft

button_style_for_theme = ft.ButtonStyle(
    bgcolor=ft.Colors.PURPLE_700,
    color=ft.Colors.AMBER_50,
    overlay_color=ft.Colors.PURPLE_300,
    elevation=6,
    shadow_color=ft.Colors.PURPLE_900,
    shape=ft.RoundedRectangleBorder(radius=16),
    padding=ft.padding.symmetric(horizontal=24, vertical=14),
)


button_style_for_play = ft.ButtonStyle(
    bgcolor=ft.Colors.GREEN_700,
    color=ft.Colors.AMBER_50,
    overlay_color=ft.Colors.GREEN_300,
    elevation=6,
    shadow_color=ft.Colors.GREEN_900,
    shape=ft.RoundedRectangleBorder(radius=16),
    padding=ft.padding.symmetric(horizontal=24, vertical=14),
)

button_style_for_delete = ft.ButtonStyle(
    bgcolor=ft.Colors.RED_700,
    color=ft.Colors.AMBER_50,
    overlay_color=ft.Colors.RED_300,
    elevation=6,
    shadow_color=ft.Colors.RED_900,
    shape=ft.RoundedRectangleBorder(radius=16),
    padding=ft.padding.symmetric(horizontal=24, vertical=14),
)

button_style_for_back = ft.ButtonStyle(
    bgcolor=ft.Colors.BLUE_700,
    color=ft.Colors.AMBER_50,
    overlay_color=ft.Colors.BLUE_300,
    elevation=6,
    shadow_color=ft.Colors.BLUE_900,
    shape=ft.RoundedRectangleBorder(radius=16),
    padding=ft.padding.symmetric(horizontal=24, vertical=14),
)


"""Text Styles"""
beautiful_text_style = ft.TextStyle(
    size=28,
    weight=ft.FontWeight.BOLD,
    color=ft.Colors.AMBER_300,
    shadow=ft.BoxShadow(
        blur_radius=6,
        color=ft.Colors.AMBER_700,
        offset=ft.Offset(2, 2),
    ),
    italic=True,
    letter_spacing=1.5,
)


