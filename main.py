mport sqlite3
import flet as ft


# Инициализация базы данных с расширенными полями
def init_db():
    conn = sqlite3.connect("tinctures_pro.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT,
            strength TEXT,
            days TEXT,
            temperature TEXT,
            comments TEXT
        )
    """)
    conn.commit()
    conn.close()


def main(page: ft.Page):
    page.title = "Рецепты настоек"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    init_db()

    # Поля ввода
    title_field = ft.TextField(
        label="Название настойки", border_radius=10, prefix_icon=ft.icons.BOOK
    )
    ingredients_field = ft.TextField(
        label="Ингредиенты (каждый с новой строки)",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_radius=10,
        prefix_icon=ft.icons.LIST,
    )
    strength_field = ft.TextField(
        label="Крепость самогона (например, 45%)",
        border_radius=10,
        prefix_icon=ft.icons.WATER_DROP,
    )
    days_field = ft.TextField(
        label="Время настаивания (дней)",
        border_radius=10,
        prefix_icon=ft.icons.TIMER,
    )
    temp_field = ft.TextField(
        label="Температура (например, комнатная, темное место)",
        border_radius=10,
        prefix_icon=ft.icons.THERMOSTAT,
    )
    comments_field = ft.TextField(
        label="Дополнительные комментарии / заметки",
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_radius=10,
        prefix_icon=ft.icons.COMMENT,
    )

    list_view = ft.ListView(expand=True, spacing=10, padding=10)

    def load_recipes(search_text=""):
        list_view.controls.clear()
        conn = sqlite3.connect("tinctures_pro.db")
        cursor = conn.cursor()

        if search_text:
            cursor.execute(
                """
                SELECT id, title, strength, days FROM recipes 
                WHERE title LIKE ? OR ingredients LIKE ?
            """,
                (f"%{search_text}%", f"%{search_text}%"),
            )
        else:
            cursor.execute("SELECT id, title, strength, days FROM recipes")

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            r_id, r_title, r_strength, r_days = row
            list_view.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Icon(
                                        ft.icons.LOCAL_BAR, color="amber"
                                    ),
                                    title=ft.Text(
                                        r_title,
                                        weight=ft.FontWeight.BOLD,
                                        size=16,
                                    ),
                                    subtitle=ft.Text(
                                        f"Крепость: {r_strength} | Выдержка: {r_days} дн."
                                    ),
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton(
                                            "Подробнее",
                                            data=r_id,
                                            on_click=view_details,
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_color="red400",
13:01
data=r_id,
                                            on_click=delete_recipe,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ]
                        ),
                        padding=10,
                    )
                )
            )
        page.update()

    def save_recipe(e):
        if not title_field.value:
            page.snack_bar = ft.SnackBar(
                ft.Text("Введите название настойки!")
            )
            page.snack_bar.open = True
            page.update()
            return

        conn = sqlite3.connect("tinctures_pro.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO recipes (title, ingredients, strength, days, temperature, comments)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                title_field.value,
                ingredients_field.value,
                strength_field.value,
                days_field.value,
                temp_field.value,
                comments_field.value,
            ),
        )
        conn.commit()
        conn.close()

        # Очистка полей
        title_field.value = ""
        ingredients_field.value = ""
        strength_field.value = ""
        days_field.value = ""
        temp_field.value = ""
        comments_field.value = ""

        page.snack_bar = ft.SnackBar(ft.Text("Рецепт успешно сохранен!"))
        page.snack_bar.open = True
        load_recipes()
        page.update()

    def view_details(e):
        r_id = e.control.data
        conn = sqlite3.connect("tinctures_pro.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, ingredients, strength, days, temperature, comments FROM recipes WHERE id = ?",
            (r_id,),
        )
        rec = cursor.fetchone()
        conn.close()

        if rec:
            dlg = ft.AlertDialog(
                title=ft.Text(rec[0], weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    [
                        ft.Text(
                            f"💧  Крепость основы: {rec[2]}",
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            f"⏳  Время настаивания: {rec[3]} дней",
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            f"🌡 Температура: {rec[4]}",
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Divider(),
                        ft.Text(
                            "Ингредиенты:",
                            weight=ft.FontWeight.BOLD,
                            color="amber",
                        ),
                        ft.Text(rec[1] if rec[1] else "Не указаны"),
                        ft.Divider(),
                        ft.Text(
                            "Комментарии:",
                            weight=ft.FontWeight.BOLD,
                            color="amber",
                        ),
                        ft.Text(rec[5] if rec[5] else "Нет комментариев"),
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton(
                        "Закрыть", on_click=lambda _: close_dlg(dlg)
                    )
                ],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

    def close_dlg(dlg):
        dlg.open = False
        page.update()

    def delete_recipe(e):
        r_id = e.control.data
        conn = sqlite3.connect("tinctures_pro.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recipes WHERE id = ?", (r_id,))
13:01
conn.commit()
        conn.close()
        load_recipes()

    def search_change(e):
        load_recipes(search_field.value)

    search_field = ft.TextField(
        label="Поиск по названию или ингредиентам",
        prefix_icon=ft.icons.SEARCH,
        border_radius=10,
        on_change=search_change,
    )

    # Вкладки: Добавление и Список
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Рецепты",
                icon=ft.icons.LIST_ALT,
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=10),
                            search_field,
                            ft.Container(height=10),
                            list_view,
                        ]
                    ),
                    padding=10,
                ),
            ),
            ft.Tab(
                text="Добавить",
                icon=ft.icons.ADD_CIRCLE,
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=10),
                            title_field,
                            strength_field,
                            days_field,
                            temp_field,
                            ingredients_field,
                            comments_field,
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                text="Сохранить рецепт",
                                icon=ft.icons.SAVE,
                                on_click=save_recipe,
                                style=ft.ButtonStyle(
                                    color=ft.colors.WHITE,
                                    bgcolor=ft.colors.GREEN_700,
                                ),
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=10,
                ),
            ),
        ],
        expand=1,
    )

    page.add(tabs)
    load_recipes()


ft.app(target=main)
