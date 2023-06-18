from __future__ import annotations

from typing import TYPE_CHECKING

from textual import log
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from rich.pretty import Pretty

from abacura.mud.options.msdp import MSDPMessage
from abacura.plugins.events import event

if TYPE_CHECKING:
    from abacura import Session
    from textual.screen import Screen
    from typing import Self

class LOKCharacter(Static):
    """Tintin-helper style character information block"""

    def compose(self) -> ComposeResult:
        yield Static("Character", classes="WidgetTitle")
        yield LOKCharacterStatic()

class LOKCharacterStatic(Static):
    """Subwidget to display current Character details"""
    character_name: reactive[str | None] = reactive[str | None](None)
    character_class: reactive[str | None] = reactive[str | None](None)
    character_level: reactive[int | None] = reactive[int | None](None)
    mud_uptime: reactive[int | None] = reactive[int | None](None)

    # TODO this could be cleaner, and potentially one-shot msdp reactives
    def on_mount(self):
        """Register event listeners, widgets are not plugins so we must
        For oneshotting this, we would need to
        * Create a reactive variable on the class, set the value to the current 
            MSDP value for the field
        * Tie the MSDP name to the variable name, perhaps by setting a dict[msdp, variable name]
        * Register a function self.msdp_update_generic to the MSDP var events
            (this could live in a parent class)
        """

        for hook in [("character_name", "CHARACTER_NAME", self.update_char_name),
                     ("character_class", "CLASS", self.update_char_class),
                     ("character_level", "LEVEL", self.update_char_level),
                     ("mud_uptime", "UPTIME", self.update_mud_uptime)]:
            # For now we'll just seed and subscribe in one shot
            self.msdp_seed_and_subscribe(*hook)
        
        #generic_hook = event(trigger="msdp_value_GOLD", priority=5)(self.generic_msdp_hook)
        #setattr(self, "update_gold", generic_hook)

    def generic_msdp_hook(self, message: MSDPMessage):
        """Generic handler for MSDP values"""
        log(f"MSDP generic event {Pretty(message.type)}")


    def msdp_seed_and_subscribe(self, local_val: str, msdp_val: str, func: callable):
        """Grab an initial value and subscribe to an @event"""
        log(f"Test subscribe to {msdp_val}")
        if 69 in self.screen.session.options and msdp_val in self.screen.session.options[69].values:
            setattr(self, local_val, self.screen.session.options[69].values[msdp_val])
        else:
            setattr(self, local_val, None)
        self.screen.session.event_manager.listener(func)

    def render(self) -> str:
        return f"{self.character_name} {self.character_class} " + \
            f"[{self.character_level}]\n{self.mud_uptime}\n" + \
            "\nStr: ONE MILLION int: wis: blah\n" + \
            f"[green]Gold: [white] [green]Bank: [white]All\n" + \
            "[green]Estimated Meta Sessions: [white]69"

    @event("msdp_value_CHARACTER_NAME")
    def update_char_name(self, message: MSDPMessage):
        self.character_name = message.value

    @event("msdp_value_CLASS")
    def update_char_class(self, message: MSDPMessage):
        self.character_class = message.value

    @event("msdp_value_LEVEL")
    def update_char_level(self, message: MSDPMessage):
        self.character_level = message.value

    @event("msdp_value_UPTIME")
    def update_mud_uptime(self, message: MSDPMessage):
        self.mud_uptime = message.value