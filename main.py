import flet as ft
import datetime

# Main Flet app
def main(page: ft.Page):
    page.title = "Real-Time Chat App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    CHAT_ROOMS_KEY = "chat_rooms"
    MESSAGES_KEY_PREFIX = "messages_"

    def fetch_chat_rooms():
        return page.client_storage.get(CHAT_ROOMS_KEY) or []

    def create_chat_room(room_name):
        chat_rooms = fetch_chat_rooms()
        if room_name not in chat_rooms:
            chat_rooms.append(room_name)
            page.client_storage.set(CHAT_ROOMS_KEY, chat_rooms)
            # Broadcast the updated chat room list to all clients
            page.pubsub.send_all(("update_chat_rooms", chat_rooms))
            return True
        return False

    def fetch_messages(room_name):
        return page.client_storage.get(f"{MESSAGES_KEY_PREFIX}{room_name}") or []

    def send_message(room_name, user, message):
        messages = fetch_messages(room_name)
        messages.append({
            "user": user,
            "message": message,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })
        page.client_storage.set(f"{MESSAGES_KEY_PREFIX}{room_name}", messages)

        page.pubsub.send_all(("new_message", (room_name, messages[-1])))


    def on_message(message):
        msg_type, payload = message
        if msg_type == "new_message":
            room_name, msg = payload
            if current_room == room_name:

                is_current_user = msg["user"] == user_name.value

                message_display.controls.append(
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(msg["user"], weight="bold"),
                                        ft.Text(msg["message"]),
                                        ft.Text(msg["timestamp"], size=12, color="white"),
                                    ],
                                    spacing=2,
                                ),
                                bgcolor="#029c9c" if is_current_user else "#2e2e2e",
                                padding=10,
                                border_radius=10,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END if is_current_user else ft.MainAxisAlignment.START,
                    )
                )
                page.update()
        elif msg_type == "update_chat_rooms":
            chat_rooms = payload
            room_dropdown.options = [ft.dropdown.Option(room) for room in chat_rooms]
            page.update()


    page.pubsub.subscribe(on_message)

    chat_rooms = fetch_chat_rooms()
    room_dropdown = ft.Dropdown(options=[ft.dropdown.Option(room) for room in chat_rooms], width=200)
    message_display = ft.Column(scroll="auto", expand=True)
    message_input = ft.TextField(hint_text="Type a message...", expand=True)
    user_name = ft.TextField(hint_text="Enter your name...", width=200)
    new_room_input = ft.TextField(hint_text="Enter new chat room name...", width=200)

    current_room = None

    def load_messages():
        if current_room:
            messages = fetch_messages(current_room)
            message_display.controls.clear()
            for msg in messages:
                is_current_user = msg["user"] == user_name.value
                message_display.controls.append(
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(msg["user"], weight="bold"),
                                        ft.Text(msg["message"]),
                                        ft.Text(msg["timestamp"], size=12, color="white"),
                                    ],
                                    spacing=2,
                                ),
                                bgcolor="#029c9c" if is_current_user else "#2e2e2e",
                                padding=10,
                                border_radius=10,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END if is_current_user else ft.MainAxisAlignment.START,
                    )
                )
            page.update()

    def on_join_room(e):
        nonlocal current_room
        current_room = room_dropdown.value
        if current_room:
            load_messages()
            join_button.text = "Leave Room"
            join_button.on_click = on_leave_room
            page.update()

    def on_leave_room(e):
        nonlocal current_room
        current_room = None
        message_display.controls.clear()
        join_button.text = "Join Room"
        join_button.on_click = on_join_room
        page.update()

    def on_send_message(e):
        room_name = current_room
        user = user_name.value
        message = message_input.value
        if room_name and user and message:
            send_message(room_name, user, message)
            message_input.value = ""
            page.update()

    # Function to handle creating a new chat room
    def on_create_room(e):
        new_room_name = new_room_input.value
        if new_room_name:
            if create_chat_room(new_room_name):
                new_room_input.value = ""
                page.update()
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Chat room already exists!"))
                page.snack_bar.open = True
                page.update()

    join_button = ft.ElevatedButton("Join Room", on_click=on_join_room)
    send_button = ft.ElevatedButton("Send", on_click=on_send_message)
    create_room_button = ft.ElevatedButton("Create Room", on_click=on_create_room)

    page.add(
        ft.Row([user_name, room_dropdown, join_button], alignment="center"),
        ft.Row([new_room_input, create_room_button], alignment="center"),
        ft.Container(message_display, border=ft.border.all(1), padding=10, width=600, height=400),
        ft.Row([message_input, send_button], alignment="center")
    )

ft.app(target=main, view=ft.WEB_BROWSER, port=2020)