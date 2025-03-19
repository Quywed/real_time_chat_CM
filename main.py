import flet as ft

class Message:
    def __init__(self, user_name: str, text: str, message_type: str, chat_room: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.chat_room = chat_room


class ChatMessage(ft.Row):
    def __init__(self, message: Message, is_current_user: bool):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

        self.alignment = ft.MainAxisAlignment.END if is_current_user else ft.MainAxisAlignment.START

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else "U"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Chat em Tempo Real"


    join_user_name = ft.TextField(
        label="Introduza o nome do seu utilizador",
        autofocus=True,
    )

    create_chat_room = ft.TextField(
        label="Introduza o nome da sala de chat",
        autofocus=False,
    )

    def create_chat_click(e):
        if not join_user_name.value.strip():
            join_user_name.error_text = "Por favor, introduza um valor válido."
            join_user_name.update()
            return

        if not create_chat_room.value.strip():
            create_chat_room.error_text = "Por favor, introduza um valor válido."
            create_chat_room.update()
            return

        user_name = join_user_name.value.strip()
        chat_room = create_chat_room.value.strip()

        # Automatically send a join message to the chat
        page.pubsub.send_all(
            Message(
                user_name=user_name,
                text=f"🟢 {user_name} criou e juntou-se ao chat '{chat_room}'.",
                message_type="chat_message",
                chat_room=chat_room,
            )
        )

        # Set the user's current chat room
        page.client_storage.set("user_name", user_name)
        page.client_storage.set("chat_room", chat_room)

        join_user_name.disabled = True
        create_chat_room.disabled = True
        create_button.disabled = True
        page.update()

    def join_chat_click(e, chat_room: str):
        user_name = page.client_storage.get("user_name")

        if not user_name:
            join_user_name.error_text = "Introduza o seu utilizador primeiro!"
            join_user_name.update()
            return

        # Set the user's current chat room
        page.client_storage.set("chat_room", chat_room)

        # Automatically send a join message to the chat
        page.pubsub.send_all(
            Message(
                user_name=user_name,
                text=f"🟢 {user_name} juntou-se ao chat '{chat_room}'.",
                message_type="chat_message",
                chat_room=chat_room,
            )
        )

        # Clear the chat history when joining a new room
        chat.controls.clear()
        page.update()

    def leave_chat_click(e):
        user_name = page.client_storage.get("user_name")
        chat_room = page.client_storage.get("chat_room")

        if user_name and chat_room:
            page.pubsub.send_all(
                Message(
                    user_name=user_name,
                    text=f"🔴 {user_name} saiu do chat '{chat_room}'.",
                    message_type="chat_message",
                    chat_room=chat_room,
                )
            )

            # Remove the user from the chat room
            page.client_storage.remove("chat_room")
            join_user_name.disabled = False
            create_chat_room.disabled = False
            create_button.disabled = False
            page.update()

    # Create button to create a new chat room
    create_button = ft.ElevatedButton(text="Criar grupo!", on_click=create_chat_click)
    leave_button = ft.ElevatedButton(text="Sair do grupo!", on_click=leave_chat_click)

    def send_message_click(e):
        user_name = page.client_storage.get("user_name")
        chat_room = page.client_storage.get("chat_room")

        if not user_name:
            join_user_name.error_text = "Introduza o seu utilizador primeiro!"
            join_user_name.update()
            return

        if not chat_room:
            create_chat_room.error_text = "Introduza a sala de chat primeiro!"
            create_chat_room.update()
            return

        if new_message.value.strip():
            page.pubsub.send_all(
                Message(
                    user_name,
                    new_message.value.strip(),
                    message_type="chat_message",
                    chat_room=chat_room,
                )
            )
            new_message.value = ""
            new_message.focus()
            page.update()

    def on_message(message: Message):
        user_name = page.client_storage.get("user_name")
        chat_room = page.client_storage.get("chat_room")

        if message.chat_room != chat_room:
            return  # Ignore messages from other chat rooms

        is_current_user = message.user_name == user_name 
        if message.message_type == "chat_message":
            if "juntou-se ao chat" in message.text or "saiu do chat" in message.text or "criou e juntou-se ao chat" in message.text:  # Check if it's a join/leave/create message
                m = ft.Text(
                    message.text,
                    italic=True,
                    weight="bold",
                    color=ft.Colors.GREEN if "juntou-se" in message.text or "criou" in message.text else ft.Colors.RED,  # Green for join/create, Red for leave
                )
            else:
                m = ChatMessage(message, is_current_user)

        else:
            m = ft.Text(message.text, italic=True, color=ft.Colors.BLACK45, size=12)
        chat.controls.append(m)
        page.update()

    page.pubsub.subscribe(on_message)

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    page.add(
        ft.Row([join_user_name, create_chat_room, create_button, leave_button], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED,
                    on_click=send_message_click,
                ),
            ]
        ),
    )


ft.app(target=main, view=ft.WEB_BROWSER, port=8080)