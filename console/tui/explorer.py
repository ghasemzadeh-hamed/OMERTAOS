"""Textual-based terminal explorer for configuring OMERTAOS Control."""

from __future__ import annotations

import argparse
from typing import Iterable, List
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, TextLog, Tree

from .api import CommandProcessor, ControlAPI


class Sidebar(Tree[None]):
    """Tree widget that shows live Control resources."""

    def update_sections(
        self,
        providers: Iterable[dict],
        modules: Iterable[dict],
        data_sources: Iterable[dict],
    ) -> None:
        root = self.root
        if root is None:
            root = self.add_root("Explorer")
        else:
            root.remove_children()
        providers_node = root.add("Providers", expand=True)
        for provider in providers:
            providers_node.add(f"{provider.get('name', '?')} ({provider.get('kind', '?')})")
        modules_node = root.add("Modules", expand=True)
        for module in modules:
            modules_node.add(f"{module.get('name', '?')}@{module.get('version', '?')}")
        datasources_node = root.add("Data Sources", expand=True)
        for ds in data_sources:
            datasources_node.add(f"{ds.get('name', '?')} ({ds.get('kind', '?')})")
        self.refresh(layout=True)


class ExplorerApp(App):
    """Main Textual application."""

    CSS_PATH = None
    BINDINGS = [Binding("ctrl+d", "show_help", "Help"), Binding("ctrl+r", "refresh", "Refresh")]

    def __init__(self, api: ControlAPI, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api = api
        self.processor = CommandProcessor(api)
        self.sidebar: Sidebar
        self.log: TextLog
        self.command_input: Input

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            self.sidebar = Sidebar("Explorer")
            self.sidebar.show_root = False
            yield self.sidebar
            with Vertical():
                self.log = TextLog(highlight=True, markup=True, wrap=True)
                self.log.write("Welcome to the OMERTAOS explorer. Type `help` to view available commands.")
                yield self.log
                self.command_input = Input(placeholder="Type a command and press Enter...")
                yield self.command_input
        yield Footer()

    async def on_mount(self) -> None:
        await self.refresh_sidebar()
        await self.command_input.focus()

    async def refresh_sidebar(self) -> None:
        providers = await self.run_in_thread(self.api.list_providers)
        modules = await self.run_in_thread(self.api.list_modules)
        data_sources = await self.run_in_thread(self.api.list_data_sources)
        self.sidebar.update_sections(providers, modules, data_sources)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value.strip()
        self.command_input.value = ""
        if not command:
            return
        self.log.write(f"[bold cyan]>[/] {command}")
        result = await self.run_in_thread(self.processor.execute, command)
        if result:
            self._write_multiline(result)
        await self.refresh_sidebar()

    def _write_multiline(self, message: str) -> None:
        for line in message.splitlines():
            self.log.write(line)

    async def action_show_help(self) -> None:
        self._write_multiline(self.processor.execute("help"))

    async def action_refresh(self) -> None:
        await self.refresh_sidebar()
        self.log.write("Sidebar refreshed.")

    async def on_resize(self, event: events.Resize) -> None:  # pragma: no cover - UI feedback
        self.log.write(f"Window resized to {event.size.width}x{event.size.height}")


def run_explorer(args: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Command explorer for aionOS")
    parser.add_argument("--api", default="http://127.0.0.1:8001", help="Control API base URL")
    parser.add_argument("--token", default=None, help="Optional bearer token")
    parser.add_argument("--no-verify", action="store_true", help="Disable TLS verification")
    parsed = parser.parse_args(args=args)
    api = ControlAPI(parsed.api, token=parsed.token, verify=not parsed.no_verify)
    ExplorerApp(api).run()


if __name__ == "__main__":  # pragma: no cover
    run_explorer()
