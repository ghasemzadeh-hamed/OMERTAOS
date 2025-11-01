"""Minimal Textual-based terminal explorer for AION OS."""
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

TABS = [
    "Projects",
    "Providers",
    "Modules",
    "DataSources",
    "Router",
    "Chat",
    "Health",
    "Logs",
    "Admin",
]


class Tab(Static):
    def __init__(self, label: str) -> None:
        super().__init__(label, classes="tab")


class ExplorerApp(App):
    CSS = """
    Screen { layout: vertical; }
    .tabs { height: 3; content-align: center middle; background: $secondary; }
    .body { flex: 1; padding: 1 2; }
    .tab { padding: 0 1; margin: 0 1; background: $panel; border: solid $accent 1; }
    .tab--active { background: $accent; color: black; }
    """

    BINDINGS = [
        ("left", "previous_tab", "Prev"),
        ("right", "next_tab", "Next"),
        ("ctrl+s", "apply", "Apply"),
        ("ctrl+e", "export", "Export"),
        ("ctrl+j", "jobs", "Jobs"),
        ("q", "quit", "Quit"),
    ]

    active_index = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes="tabs"):
            for tab in TABS:
                yield Tab(tab)
        yield Static(self._content_for_tab(), classes="body")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_tabs()

    def watch_active_index(self, _: int) -> None:
        self._refresh_tabs()

    def _refresh_tabs(self) -> None:
        for index, widget in enumerate(self.query(Tab)):
            if index == self.active_index:
                widget.add_class("tab--active")
            else:
                widget.remove_class("tab--active")
        body = self.query_one(".body", Static)
        body.update(self._content_for_tab())

    def _content_for_tab(self) -> str:
        current = TABS[self.active_index]
        if current == "Chat":
            return "Chat Config Bot: describe your intent to call control APIs."
        if current == "Providers":
            return "List and manage providers via /api/providers endpoints."
        if current == "Modules":
            return "Attach, enable, upgrade, and rollback modules."
        if current == "DataSources":
            return "Manage connectors and run health checks."
        if current == "Router":
            return "View or update router policies and reload routes."
        if current == "Health":
            return "Monitor health summary from /api/health."
        if current == "Logs":
            return "Stream worker jobs from /api/jobs."
        if current == "Admin":
            return "Generate tokens and manage RBAC roles."
        return "Project overview and bundle status."

    def action_previous_tab(self) -> None:
        self.active_index = (self.active_index - 1) % len(TABS)

    def action_next_tab(self) -> None:
        self.active_index = (self.active_index + 1) % len(TABS)

    def action_apply(self) -> None:
        self.bell()
        self.toast("Apply triggered (Ctrl+S)")

    def action_export(self) -> None:
        self.bell()
        self.toast("Export triggered (Ctrl+E)")

    def action_jobs(self) -> None:
        self.bell()
        self.toast("Job viewer opened (Ctrl+J)")


if __name__ == "__main__":  # pragma: no cover
    ExplorerApp().run()
