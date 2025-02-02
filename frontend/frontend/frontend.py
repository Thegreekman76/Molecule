"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config


class State(rx.State):
    """The app state."""

    ...


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Molecule Framework esa!", size="9"),
            rx.text("¡Frontend funcionando correctamente!"),
            spacing="4",
        ),
        height="100vh",
    )


app = rx.App()
app.add_page(index, route="/")
