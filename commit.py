"""
@file: commit.py
@brief: This file implements a commit preprocessor to use conventional commit messages. It provides a simple TUI to create meaningful and structured commit messages.
@author: Nicolas Lesquoy
@date: 2025-08-03 (project creation date)
"""

# Python standard library imports
import subprocess

# Third-party imports
from textual.app import App, ComposeResult
from textual.widgets import Input, Static, ListView, ListItem, Label, Checkbox
from textual.containers import Vertical, Horizontal
from textual.binding import Binding


class CommitTUI(App):
    """A TUI for creating conventional commit messages."""

    CSS_PATH = "style.css"  # Style definition for the TUI

    BINDINGS = [
        Binding("escape", "app.quit", "Quit", show=False),
        Binding("ctrl+c", "app.quit", "Quit", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.commit_types = [
            ("feat", "A new feature"),
            ("fix", "A bug fix"),
            ("docs", "Documentation only changes"),
            ("refactor", "A code change that neither fixes a bug nor adds a feature"),
            ("style", "Changes that do not affect the meaning of the code"),
            ("test", "Adding missing tests or correcting existing tests"),
            ("chore", "Changes to the build process or auxiliary tools"),
        ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("What change would you like to commit?")
            with Horizontal():
                yield Input(placeholder="Enter commit summary", id="msg")
                yield Checkbox("Is this a breaking change?", id="breaking_change")

            yield Static("Scope (optional):")
            yield Input(placeholder="e.g., 'renderer', 'api'", id="scope")

            yield Static("Select the type of change:")
            list_items = []
            for commit_type, description in self.commit_types:
                list_items.append(
                    ListItem(Label(f"  {commit_type}: {description}"), id=commit_type)
                )
            yield ListView(*list_items, id="commit_types")

    def on_mount(self) -> None:
        """Focus the input on startup."""
        self.query_one("#msg", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Move focus when Enter is pressed on an input."""
        if event.input.id == "msg" and event.input.value.strip():
            self.query_one("#scope", Input).focus()
        elif event.input.id == "scope":
            self.query_one(ListView).focus()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """When a list item is selected, submit the form."""
        msg = self.query_one("#msg", Input).value.strip()
        commit_type = event.item.id
        is_breaking = self.query_one("#breaking_change", Checkbox).value
        scope = self.query_one("#scope", Input).value.strip()
        if msg and commit_type:
            breaking_indicator = "!" if is_breaking else ""
            scope_part = f"({scope})" if scope else ""
            self.exit(f"{commit_type}{scope_part}{breaking_indicator}: {msg}")


def commit():
    """Run the commit TUI and performs the necessary git operations."""
    commit_tui = CommitTUI()
    commit_message = commit_tui.run()
    if commit_message:
        cmd_add = ["git", "add", "."]
        cmd_commit = ["git", "commit", "-m", commit_message]
        try:
            subprocess.run(cmd_add, check=True)
            subprocess.run(cmd_commit, check=True)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        else:
            print("Changes staged and committed successfully.")


if __name__ == "__main__":
    commit()
