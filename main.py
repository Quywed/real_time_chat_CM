import flet as ft
import datetime

# Main Flet app
def main(page: ft.Page):
    # At the beginning of main function, update page settings
    page.title = "Real-Time Chat App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"
    page.padding = 20

    # Define our views
    chat_view = ft.Column()
    users_view = ft.Column(
        [
            ft.Text("Registered Users", size=30, weight="bold"),
            ft.ListView(expand=True)
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=20,
        visible=False
    )
    
    # Storage keys
    REGISTERED_USERS_KEY = "registered_users"
    CHAT_ROOMS_KEY = "chat_rooms"
    PUBLIC_MESSAGES_KEY_PREFIX = "public_messages_"
    PRIVATE_MESSAGES_KEY_PREFIX = "private_messages_"

    def get_registered_users():
        users = page.client_storage.get(REGISTERED_USERS_KEY)
        if users is None:
            return []
        try:
            if isinstance(users, str):
                return eval(users) if users else []
            return users if isinstance(users, list) else []
        except:
            return []

    def add_registered_user(username):
        if not username:
            return False
        users = get_registered_users()
        clean_username = username.replace("'", "").replace('"', '').replace("\\", "")
        if clean_username not in users:
            users.append(clean_username)
            page.client_storage.set(REGISTERED_USERS_KEY, users)
            page.pubsub.send_all(("update_users", users))
            return True
        return False
    
    def update_users_view(users=None):
        if users is None:
            users = get_registered_users()
        users_view.controls[1].controls.clear()
        for user in sorted(users):
            if user != user_name.value:
                users_view.controls[1].controls.append(
                    ft.ListTile(
                        title=ft.Text(user),
                        leading=ft.Icon(ft.icons.PERSON),
                        on_click=lambda e, u=user: start_private_chat(e, u),
                    )
                )
        if users_view.visible:
            page.update()

    def start_private_chat(e, recipient):
        nonlocal current_room, is_private_chat
        participants = sorted([user_name.value, recipient])
        current_room = f"private_{participants[0]}_{participants[1]}"
        is_private_chat = True
        private_recipient.value = recipient
        private_chat_header.visible = True
        back_to_public_button.visible = True
        load_messages()
        chat_view.visible = True
        users_view.visible = False
        page.update()

    # Navigation function
    def navigate(e):
        chat_view.visible = not chat_view.visible
        users_view.visible = not users_view.visible
        if users_view.visible:
            update_users_view()
        page.update()

    # Navigation buttons
    nav_button = ft.IconButton(
        icon=ft.icons.PEOPLE,
        on_click=navigate,
        tooltip="View Registered Users"
    )
    
    back_to_public_button = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        on_click=lambda e: return_to_public_chat(e),
        tooltip="Back to Public Chat",
        visible=False
    )

    def return_to_public_chat(e):
        nonlocal current_room, is_private_chat
        current_room = None
        is_private_chat = False
        private_recipient.value = ""
        private_chat_header.visible = False
        message_display.controls.clear()
        back_to_public_button.visible = False
        page.update()

    # Chat components
    chat_rooms = page.client_storage.get(CHAT_ROOMS_KEY) or []
    room_dropdown = ft.Dropdown(options=[ft.dropdown.Option(room) for room in chat_rooms], width=200)
    message_display = ft.Column(scroll="auto", expand=True)
    message_input = ft.TextField(hint_text="Type a message...", expand=True)
    user_name = ft.TextField(hint_text="Enter your name...", width=200)
    new_room_input = ft.TextField(hint_text="Enter new chat room name...", width=200)
    room_dropdown = ft.Dropdown(options=[ft.dropdown.Option(room) for room in chat_rooms], width=200, disabled=True)
    
    # Private chat components
    private_recipient = ft.Text("", size=16, weight="bold")
    private_chat_header = ft.Row(
        [
            ft.Text("Private chat with: "),
            private_recipient,
            back_to_public_button
        ],
        visible=False
    )

    current_room = None
    is_private_chat = False
    is_user_created = False

    def fetch_messages(room_name, is_private=False):
        prefix = PRIVATE_MESSAGES_KEY_PREFIX if is_private else PUBLIC_MESSAGES_KEY_PREFIX
        return page.client_storage.get(f"{prefix}{room_name}") or []

    def send_message(room_name, user, message, is_private=False, is_system=False):
        prefix = PRIVATE_MESSAGES_KEY_PREFIX if is_private else PUBLIC_MESSAGES_KEY_PREFIX
        messages = fetch_messages(room_name, is_private)
        messages.append({
            "id": len(messages),
            "user": user,
            "message": message,
            "timestamp": datetime.datetime.now().strftime("%H:%M"),
            "is_private": is_private,
            "is_system": is_system
        })
        page.client_storage.set(f"{prefix}{room_name}", messages)
        page.pubsub.send_all(("new_message", (room_name, messages[-1], is_private)))

    def create_message_row(msg, is_current_user):
        if msg.get("is_system"):
            # System message styling
            return ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(msg["message"], size=12, color="gray", italic=True),
                            ],
                            spacing=2,
                            horizontal_alignment="center"
                        ),
                        padding=5,
                        width=600
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        
        bg_color = "#029c9c" if is_current_user else "#2e2e2e"
        if msg.get("is_private"):
            bg_color = "#5c029c" if is_current_user else "#4e2e5e"
            
        message_row = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(msg["user"], weight="bold"),
                            ft.Text(msg["message"], key=f"message_{msg['id']}"),
                            ft.Text(msg["timestamp"], size=12, color="white"),
                        ],
                        spacing=2,
                    ),
                    bgcolor=bg_color,
                    padding=10,
                    border_radius=10,
                )
            ],
            alignment=ft.MainAxisAlignment.END if is_current_user else ft.MainAxisAlignment.START,
        )
        
        if is_current_user and not msg.get("is_system"):
            edit_field = ft.TextField(visible=False, value=msg["message"])
            
            def toggle_edit(e):
                edit_field.visible = not edit_field.visible
                page.update()
                
            def save_edit(e):
                if edit_field.value != msg["message"]:
                    edit_message(current_room, msg["id"], edit_field.value, msg.get("is_private", False))
                edit_field.visible = False
                page.update()
                
            edit_button = ft.IconButton(
                icon=ft.icons.EDIT,
                on_click=toggle_edit,
                icon_color="white",
            )
            
            save_button = ft.IconButton(
                icon=ft.icons.SAVE,
                on_click=save_edit,
                icon_color="white",
            )
            
            message_row.controls.append(
                ft.Column([
                    ft.Row([edit_button, save_button]),
                    edit_field
                ])
            )
        
        return message_row

    def edit_message(room_name, message_id, new_message, is_private=False):
        prefix = PRIVATE_MESSAGES_KEY_PREFIX if is_private else PUBLIC_MESSAGES_KEY_PREFIX
        messages = fetch_messages(room_name, is_private)
        for msg in messages:
            if msg["id"] == message_id:
                msg["message"] = new_message
                msg["timestamp"] = f"{datetime.datetime.now().strftime('%H:%M')} (edited)"
                page.client_storage.set(f"{prefix}{room_name}", messages)
                page.pubsub.send_all(("edit_message", (room_name, msg, is_private)))
                break

    def clear_messages(room_name, is_private=False):
        prefix = PRIVATE_MESSAGES_KEY_PREFIX if is_private else PUBLIC_MESSAGES_KEY_PREFIX
        page.client_storage.set(f"{prefix}{room_name}", [])
        page.pubsub.send_all(("clear_messages", (room_name, is_private)))

    def on_message(message):
        msg_type, payload = message
        if msg_type == "new_message":
            room_name, msg, is_private = payload
            if not is_private and current_room == room_name:
                is_current_user = msg["user"] == user_name.value
                message_display.controls.append(create_message_row(msg, is_current_user))
                page.update()
            elif is_private:
                participants = room_name.split('_')[1:]
                if user_name.value in participants:
                    if current_room == room_name or current_room is None:
                        is_current_user = msg["user"] == user_name.value
                        message_display.controls.append(create_message_row(msg, is_current_user))
                        page.update()
        elif msg_type == "edit_message":
            room_name, msg, is_private = payload
            # Skip system messages (they can't be edited)
            if msg.get("is_system"):
                return
                
            if not is_private and current_room == room_name:
                for control in message_display.controls:
                    # Skip rows that don't have the expected structure (like system messages)
                    if (len(control.controls) > 0 and 
                        hasattr(control.controls[0], 'content') and 
                        len(control.controls[0].content.controls) > 2):
                        message_text = control.controls[0].content.controls[1]
                        if hasattr(message_text, 'key') and message_text.key == f"message_{msg['id']}":
                            message_text.value = msg["message"]
                            control.controls[0].content.controls[2].value = msg["timestamp"]
                            page.update()
                            break
            elif is_private and user_name.value in room_name.split('_')[1:]:
                for control in message_display.controls:
                    # Skip rows that don't have the expected structure (like system messages)
                    if (len(control.controls) > 0 and 
                        hasattr(control.controls[0], 'content') and 
                        len(control.controls[0].content.controls) > 2):
                        message_text = control.controls[0].content.controls[1]
                        if hasattr(message_text, 'key') and message_text.key == f"message_{msg['id']}":
                            message_text.value = msg["message"]
                            control.controls[0].content.controls[2].value = msg["timestamp"]
                            page.update()
                            break
        elif msg_type == "clear_messages":
            room_name, is_private = payload
            if (not is_private and current_room == room_name) or (is_private and current_room == room_name):
                message_display.controls.clear()
                page.update()
        elif msg_type == "update_chat_rooms":
            chat_rooms = payload
            room_dropdown.options = [ft.dropdown.Option(room) for room in chat_rooms]
            page.update()
        elif msg_type == "update_users":
            update_users_view(payload)

    page.pubsub.subscribe(on_message)

    def on_create_user(e):
        nonlocal is_user_created
        if user_name.value:
            is_user_created = True
            user_name.disabled = True
            create_user_button.disabled = True
            room_dropdown.disabled = False
            join_button.disabled = False
            if add_registered_user(user_name.value.strip()):
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Welcome, {user_name.value}!"))
                page.snack_bar.open = True
            page.update()
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text("Please enter a username!"))
            page.snack_bar.open = True
            page.update()

    def cleanup_storage():
        current = page.client_storage.get(REGISTERED_USERS_KEY)
        if isinstance(current, str):
            try:
                cleaned = eval(current) if current else []
                if isinstance(cleaned, list):
                    page.client_storage.set(REGISTERED_USERS_KEY, cleaned)
                    return cleaned
            except:
                pass
            page.client_storage.set(REGISTERED_USERS_KEY, [])
            return []
        return current if isinstance(current, list) else []

    def load_messages():
        if current_room:
            messages = fetch_messages(current_room, is_private_chat)
            message_display.controls.clear()
            for msg in messages:
                is_current_user = msg["user"] == user_name.value
                message_display.controls.append(create_message_row(msg, is_current_user))
            page.update()

    def on_join_room(e):
        nonlocal current_room, is_private_chat
        if current_room:  # If already in a room, leave it first
            send_message(current_room, "System", f"{user_name.value} left the room", is_private=False, is_system=True)
        
        current_room = room_dropdown.value
        is_private_chat = False
        private_chat_header.visible = False
        back_to_public_button.visible = False
        if current_room:
            load_messages()
            join_button.text = "Leave Room"
            join_button.on_click = on_leave_room
            send_message(current_room, "System", f"{user_name.value} joined the room", is_private=False, is_system=True)
            page.update()

    def on_leave_room(e):
        nonlocal current_room, is_private_chat
        if current_room:
            send_message(current_room, "System", f"{user_name.value} left the room", is_private=False, is_system=True)
        current_room = None
        is_private_chat = False
        private_chat_header.visible = False
        back_to_public_button.visible = False
        message_display.controls.clear()
        join_button.text = "Join Room"
        join_button.on_click = on_join_room
        page.update()

    def on_send_message(e):
        room_name = current_room
        user = user_name.value
        message = message_input.value
        if room_name and user and message:
            send_message(room_name, user, message, is_private_chat)
            message_input.value = ""
            page.update()

    def fetch_chat_rooms():
        return page.client_storage.get(CHAT_ROOMS_KEY) or []

    def create_chat_room(room_name):
        chat_rooms = fetch_chat_rooms()
        if room_name not in chat_rooms:
            chat_rooms.append(room_name)
            page.client_storage.set(CHAT_ROOMS_KEY, chat_rooms)
            page.pubsub.send_all(("update_chat_rooms", chat_rooms))
            return True
        return False

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

    join_button = ft.ElevatedButton("Join Room", on_click=on_join_room, disabled=True)
    send_button = ft.ElevatedButton("Send", on_click=on_send_message)
    clear_button = ft.ElevatedButton(
        "Clear Chat",
        on_click=lambda e: clear_messages(current_room, is_private_chat) if current_room else None,
        tooltip="Clear all messages in this chat"
    )
    create_room_button = ft.ElevatedButton("Create Room", on_click=on_create_room)
    create_user_button = ft.ElevatedButton("Create User", on_click=on_create_user)

    # Update chat_view.controls with centered alignment
    chat_view.controls = [
        ft.Column(
            [
                ft.Row([user_name, create_user_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([room_dropdown, join_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([new_room_input, create_room_button], alignment=ft.MainAxisAlignment.CENTER),
                private_chat_header,
                ft.Container(
                    message_display,
                    border=ft.border.all(1),
                    padding=10,
                    width=600,
                    height=400,
                    alignment=ft.alignment.center
                ),
                ft.Row(
                    [message_input, send_button, clear_button],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    ]

    # Update the final page.add with center alignment
    page.add(
        ft.Column(
            [
                ft.Row([nav_button, back_to_public_button], alignment=ft.MainAxisAlignment.END),
                chat_view,
                users_view
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

    update_users_view()
    cleanup_storage()

ft.app(target=main, view=ft.WEB_BROWSER, port=2020)
