#!/usr/bin/env python3
"""
Mistral CLI - TUI (Text User Interface) mit Textual
"""

import os
import sys
import json
import subprocess
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Input, Button, TabbedContent, TabPane,
    DataTable, Label, RichLog
)
from textual.binding import Binding
from textual import on
from mistralai import Mistral


# ASCII Logo für Mistral CLI
LOGO = r"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                            ┃
┃  ███╗   ███╗██╗███████╗████████╗██████╗  █████╗ ██╗       ┃
┃  ████╗ ████║██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║       ┃
┃  ██╔████╔██║██║███████╗   ██║   ██████╔╝███████║██║       ┃
┃  ██║╚██╔╝██║██║╚════██║   ██║   ██╔══██╗██╔══██║██║       ┃
┃  ██║ ╚═╝ ██║██║███████║   ██║   ██║  ██║██║  ██║███████╗  ┃
┃  ╚═╝     ╚═╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝  ┃
┃                                                            ┃
┃                  C L I   T O O L                          ┃
┃                                                            ┃
┃      Command-Line Application for Mistral AI              ┃
┃          with Extended Tool Functions                     ┃
┃                                                            ┃
┃            ⚠️  UNOFFICIAL VERSION  ⚠️                     ┃
┃                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

# Kompaktes Logo für Chat-Tab
COMPACT_LOGO = r"""
┌───────────────────────────────────────────────────┐
│ ███╗   ███╗██╗███████╗████████╗██████╗  █████╗ ██╗│
│ ████╗ ████║██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║│
│ ██╔████╔██║██║███████╗   ██║   ██████╔╝███████║██║│
│ ██║╚██╔╝██║██║╚════██║   ██║   ██╔══██╗██╔══██║██║│
│ ██║ ╚═╝ ██║██║███████║   ██║   ██║  ██║██║  ██║███║│
│ ╚═╝     ╚═╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══╝│
│        CLI TOOL - ⚠️ UNOFFICIAL VERSION ⚠️         │
└───────────────────────────────────────────────────┘
"""


# Import der Tool-Funktionen aus mistral_tools
from mistral_tools import TOOLS, execute_tool


class MistralTUI(App):
    """Hauptanwendung für Mistral CLI TUI"""

    CSS = """
    Screen {
        background: $surface;
    }

    #logo {
        height: auto;
        width: 100%;
        content-align: center middle;
        color: $accent;
        border: solid $primary;
        margin: 1;
    }

    #chat_logo {
        height: auto;
        width: 100%;
        content-align: center middle;
        color: $accent;
        border: solid $primary;
        margin: 1 0;
    }

    .chat-container {
        height: 1fr;
        border: solid $primary;
    }

    .chat-log {
        height: 1fr;
        border: solid $accent;
        background: $surface;
    }

    .input-area {
        height: auto;
        dock: bottom;
    }

    .tool-log {
        height: 15;
        border: solid yellow;
        background: $surface;
        margin-top: 1;
    }

    Button {
        margin: 1;
    }

    .settings-container {
        height: auto;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }

    DataTable {
        height: 1fr;
    }

    Input {
        margin: 1;
    }

    Label {
        margin: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+c", "clear_chat", "Clear Chat"),
    ]

    def __init__(self):
        super().__init__()
        self.client = None
        self.chat_messages = []
        self.current_model = "mistral-small-latest"
        self.temperature = 0.7
        self.max_tokens = 1024

    def compose(self) -> ComposeResult:
        """Erstelle die UI-Komponenten"""
        yield Header(show_clock=True)

        # Logo
        yield Static(LOGO, id="logo")

        # Tab-Container für verschiedene Modi
        with TabbedContent(initial="chat"):
            # Chat Tab
            with TabPane("💬 Chat", id="chat"):
                yield from self._compose_chat_tab()

            # Exec Tab
            with TabPane("⚡ Exec", id="exec"):
                yield from self._compose_exec_tab()

            # Models Tab
            with TabPane("🔧 Models", id="models"):
                yield from self._compose_models_tab()

            # Complete Tab
            with TabPane("📝 Complete", id="complete"):
                yield from self._compose_complete_tab()

            # Settings Tab
            with TabPane("⚙️ Settings", id="settings"):
                yield from self._compose_settings_tab()

        yield Footer()

    def _compose_chat_tab(self):
        """Chat-Tab Komponenten"""
        with Vertical(classes="chat-container"):
            yield Label("Chat with Tool Support - Available: Bash, Files, Web, JSON/CSV, Images")
            yield RichLog(id="chat_log", classes="chat-log", wrap=True, highlight=True)
            yield RichLog(id="tool_log", classes="tool-log", wrap=True)
            with Horizontal(classes="input-area"):
                yield Input(placeholder="Your message...", id="chat_input")
                yield Button("Send", id="chat_send", variant="primary")

    def _compose_exec_tab(self):
        """Exec-Tab Komponenten"""
        with Vertical():
            yield Label("Bash Command Generation and Execution")
            yield Input(placeholder="Describe the task...", id="exec_input")
            yield Button("Generate Commands", id="exec_generate", variant="success")
            yield RichLog(id="exec_log", classes="chat-log", wrap=True)
            with Horizontal():
                yield Button("Execute", id="exec_run", variant="warning")
                yield Button("Cancel", id="exec_cancel", variant="error")

    def _compose_models_tab(self):
        """Models-Tab Komponenten"""
        with Vertical():
            yield Label("Available Mistral Models")
            yield Button("Load Models", id="models_load", variant="primary")
            yield DataTable(id="models_table")

    def _compose_complete_tab(self):
        """Complete-Tab Komponenten"""
        with Vertical():
            yield Label("Text Completion")
            yield Input(placeholder="Your prompt...", id="complete_input")
            yield Button("Complete", id="complete_send", variant="primary")
            yield RichLog(id="complete_log", classes="chat-log", wrap=True)

    def _compose_settings_tab(self):
        """Settings-Tab Komponenten"""
        with Vertical(classes="settings-container"):
            yield Label(f"Current Model: {self.current_model}")
            yield Input(
                placeholder="Enter model name...",
                id="model_input",
                value=self.current_model
            )
            yield Label(f"Temperature: {self.temperature}")
            yield Input(
                placeholder="0.0 - 1.0",
                id="temp_input",
                value=str(self.temperature)
            )
            yield Label(f"Max Tokens: {self.max_tokens}")
            yield Input(
                placeholder="Max Tokens",
                id="tokens_input",
                value=str(self.max_tokens)
            )
            yield Button("Save Settings", id="settings_save", variant="success")
            yield Label(id="settings_status")

    def on_mount(self) -> None:
        """Wird beim Start der App aufgerufen"""
        # Initialisiere Mistral Client
        api_key = os.environ.get('MISTRAL_API_KEY')
        if not api_key:
            self.exit(message="ERROR: MISTRAL_API_KEY not set!\n" +
                     "Please set: export MISTRAL_API_KEY='your-api-key'")

        self.client = Mistral(api_key=api_key)

        # Willkommensnachricht im Chat
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.write("✨ Welcome to Mistral CLI!")
        chat_log.write(f"🤖 Model: {self.current_model}")
        chat_log.write("💡 Tip: Use tabs above to switch between different modes\n")

    @on(Button.Pressed, "#chat_send")
    async def send_chat_message(self) -> None:
        """Sende Chat-Nachricht"""
        chat_input = self.query_one("#chat_input", Input)
        message = chat_input.value.strip()

        if not message:
            return

        chat_log = self.query_one("#chat_log", RichLog)
        tool_log = self.query_one("#tool_log", RichLog)

        # Zeige Benutzernachricht
        chat_log.write(f"\n👤 You: {message}")
        chat_input.value = ""

        # Füge zu Messages hinzu
        self.chat_messages.append({"role": "user", "content": message})

        try:
            # API-Anfrage
            chat_log.write("🤔 Mistral is thinking...")

            response = self.client.chat.complete(
                model=self.current_model,
                messages=self.chat_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=TOOLS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Prüfe auf Tool Calls
            if assistant_message.tool_calls:
                tool_log.write("\n🔧 Executing tools:")

                # Füge Assistant-Nachricht hinzu
                self.chat_messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": assistant_message.tool_calls
                })

                # Führe Tools aus
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    tool_log.write(f"▶️ {tool_name}: {tool_args}")

                    # Tool ausführen (auto-confirm für TUI)
                    tool_result = execute_tool(tool_name, tool_args, auto_confirm=True)

                    tool_log.write(f"✅ Result: {json.dumps(tool_result, ensure_ascii=False)[:200]}")

                    # Tool-Ergebnis zu Messages hinzufügen
                    self.chat_messages.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                        "tool_call_id": tool_call.id
                    })

                # Zweite API-Anfrage
                response = self.client.chat.complete(
                    model=self.current_model,
                    messages=self.chat_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=TOOLS,
                    tool_choice="auto"
                )

                assistant_message = response.choices[0].message

            # Zeige finale Antwort
            if assistant_message.content:
                self.chat_messages.append({"role": "assistant", "content": assistant_message.content})
                chat_log.write(f"\n🤖 Mistral: {assistant_message.content}")

        except Exception as e:
            chat_log.write(f"\n❌ Error: {str(e)}")

    @on(Input.Submitted, "#chat_input")
    async def on_chat_input_submitted(self) -> None:
        """Wenn Enter im Chat-Input gedrückt wird"""
        await self.send_chat_message()

    @on(Button.Pressed, "#exec_generate")
    async def generate_exec_commands(self) -> None:
        """Generiere Bash-Befehle"""
        exec_input = self.query_one("#exec_input", Input)
        task = exec_input.value.strip()

        if not task:
            return

        exec_log = self.query_one("#exec_log", RichLog)
        exec_log.write(f"\n📋 Task: {task}")
        exec_log.write("🤔 Generating commands...")

        system_prompt = """You are a Bash expert. Generate executable Bash commands for the given task.

IMPORTANT:
- Output ONLY the Bash commands, no explanations
- Each command on a separate line
- Do not use Markdown code blocks
- Start directly with the commands"""

        try:
            response = self.client.chat.complete(
                model=self.current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                temperature=0.3,
                max_tokens=self.max_tokens
            )

            commands_text = response.choices[0].message.content.strip()

            # Speichere Commands für Ausführung
            self.pending_commands = [
                cmd.strip() for cmd in commands_text.split('\n')
                if cmd.strip() and not cmd.strip().startswith('#')
            ]

            exec_log.write("\n✅ Generated Commands:")
            exec_log.write("─" * 50)
            for i, cmd in enumerate(self.pending_commands, 1):
                exec_log.write(f"{i}. {cmd}")
            exec_log.write("─" * 50)
            exec_log.write("⚠️ Click 'Execute' to run the commands")

        except Exception as e:
            exec_log.write(f"\n❌ Error: {str(e)}")

    @on(Button.Pressed, "#exec_run")
    async def run_exec_commands(self) -> None:
        """Führe generierte Befehle aus"""
        if not hasattr(self, 'pending_commands') or not self.pending_commands:
            return

        exec_log = self.query_one("#exec_log", RichLog)
        exec_log.write("\n⚡ Executing commands...\n")

        for i, cmd in enumerate(self.pending_commands, 1):
            exec_log.write(f"[{i}/{len(self.pending_commands)}] {cmd}")

            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    timeout=30
                )

                if result.stdout:
                    exec_log.write(f"  ✅ {result.stdout.strip()}")
                if result.stderr:
                    exec_log.write(f"  ⚠️ {result.stderr.strip()}")
                if result.returncode != 0:
                    exec_log.write(f"  ❌ Exit Code: {result.returncode}")

            except Exception as e:
                exec_log.write(f"  ❌ Error: {str(e)}")

        exec_log.write("\n✅ All commands executed!")
        self.pending_commands = []

    @on(Button.Pressed, "#exec_cancel")
    def cancel_exec_commands(self) -> None:
        """Abbrechen"""
        self.pending_commands = []
        exec_log = self.query_one("#exec_log", RichLog)
        exec_log.write("\n⛔ Execution cancelled")

    @on(Button.Pressed, "#models_load")
    async def load_models(self) -> None:
        """Lade verfügbare Modelle"""
        table = self.query_one("#models_table", DataTable)
        table.clear(columns=True)

        table.add_column("Model ID", width=40)
        table.add_column("Description", width=60)

        try:
            models = self.client.models.list()

            for model in models.data:
                description = getattr(model, 'description', 'No description') or 'No description'
                table.add_row(model.id, description)

        except Exception as e:
            table.add_row("Error", str(e))

    @on(Button.Pressed, "#complete_send")
    async def send_complete_request(self) -> None:
        """Sende Completion-Request"""
        complete_input = self.query_one("#complete_input", Input)
        prompt = complete_input.value.strip()

        if not prompt:
            return

        complete_log = self.query_one("#complete_log", RichLog)
        complete_log.write(f"\n📝 Prompt: {prompt}")
        complete_log.write("🤔 Generating response...")

        try:
            response = self.client.chat.complete(
                model=self.current_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            result = response.choices[0].message.content
            complete_log.write(f"\n✅ Response:\n{result}\n")

        except Exception as e:
            complete_log.write(f"\n❌ Error: {str(e)}")

    @on(Button.Pressed, "#settings_save")
    def save_settings(self) -> None:
        """Speichere Einstellungen"""
        model_input = self.query_one("#model_input", Input)
        temp_input = self.query_one("#temp_input", Input)
        tokens_input = self.query_one("#tokens_input", Input)
        status_label = self.query_one("#settings_status", Label)

        try:
            self.current_model = model_input.value.strip()
            self.temperature = float(temp_input.value)
            self.max_tokens = int(tokens_input.value)

            status_label.update("✅ Settings saved!")

            # Update Labels
            labels = self.query("Label")
            for label in labels:
                if "Current Model" in str(label.renderable):
                    label.update(f"Current Model: {self.current_model}")
                elif "Temperature" in str(label.renderable):
                    label.update(f"Temperature: {self.temperature}")
                elif "Max Tokens" in str(label.renderable):
                    label.update(f"Max Tokens: {self.max_tokens}")

        except Exception as e:
            status_label.update(f"❌ Error: {str(e)}")

    def action_quit(self) -> None:
        """Beende die Anwendung"""
        self.exit()

    def action_clear_chat(self) -> None:
        """Lösche Chat-Historie"""
        self.chat_messages = []
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.clear()
        chat_log.write("🗑️ Chat history cleared")


def run_tui():
    """Starte die TUI-Anwendung"""
    app = MistralTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
