from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Input, Static

class ShinseinaSearchApp(App):
    CSS_PATH = None  # We’re not doing custom styling yet

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Type your search query and press Enter...", id="search_box")
        yield Static("Results will appear here.", id="results_panel")
        yield Footer()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        print(f"[DEBUG] Input submitted: {message.value}")
        user_query = message.value
        self.query_one("#results_panel", Static).update(f"You typed: {user_query}")

if __name__ == "__main__":
    ShinseinaSearchApp().run()
