"""LOK Communications plugins"""
from __future__ import annotations
from typing import Optional
from rich.text import Text
import re

from textual.widgets import TextLog

from abacura.mud import OutputMessage
from abacura.plugins import action
from abacura_kallisti.plugins import LOKPlugin

class LOKComms(LOKPlugin):
    comms_textlog: Optional[TextLog] = None

    #<Gossip: Taszlehoff (Shade)> 'morning'
    @action(r"^<(\w+): (\w+)( \(.*\))?> '(.*)'", color=False)
    def comms_common(self, channel: str, speaker: str, account: str, message: str, msg: OutputMessage):
        """Send common pattern comms to the commslog, including clan chat"""
        if account == None:
            account = 'None'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))
    
    #<Market: the MGSE supervisor> 'Lapis Lazuli stocks went up 10.  Trading at 130 now.'
    # Market info is a different pattern and gets different channel assignment
    @action (r"^<Market: the MGSE supervisor> (.*)", color=False)
    def comms_market_info(self, msg: OutputMessage):
        channel = 'market_info'
        speaker = 'MGSE'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    #**Whitechain: 'huehuehue'
    @action (r"(^\*\*(\w+): '(.*'))", color=False)
    def comms_group_other(self, speaker: str, message: str, msg: OutputMessage):
        channel = 'group'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    #You grouptell: huehuehue
    @action (r"You grouptell: (.*)$", color=False)
    def comms_group_self(self, message: str, msg: OutputMessage):
        channel = 'group'
        speaker = 'You'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    """
    This case: <Clan: Atropa> 'huehue' is caught by comms_common
    This method covers this case: You cchat, 'huehue'
    """
    @action(r"^(You) cchat, '(.*)'", color=False)
    def comms_clan_self(self, speaker: str, message: str, msg: OutputMessage):
        channel = 'clan'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message)) 

    @action(r"^{RolePlay: (\w+)} '(.*)'", color=False)
    def comms_roleplay(self, speaker: str, message: str, msg: OutputMessage):
        channel = 'roleplay'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message)) 

    @action(r"^<Gemote> '(.*)'", color=False)
    def comms_gemote(self, msg: OutputMessage):
        """Gemote speaker is indeterminate"""
        channel = 'gemote'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message)) 
    
    #You shout, 'huehue'
    #Whitechain shouts, 'huehue'
    @action(r"^(\w+) (shout|shouts), '(.*)'", color=False)
    def comms_shout(self, speaker: str, verb: str, message: str, msg: OutputMessage):
        channel = 'shout'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    #yell has a comma when others yell, not when self yells
    @action(r"^(\w+) (yell|yells,) '(.*)'", color=False)
    def comms_yell(self, speaker: str, verb: str, message: str, msg: OutputMessage):
        channel = 'yell'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    """
    immchat, imms only
    [Whitechain:(Vajra)] 'blurp'
    [Vajra:] 'blurp'
    [Vajra:(?)] 'blurp'
    """
    @action(r"^\[(\w+):(\(.*\)+)?] '(.*)'", color=False)
    def comms_immchat(self, speaker: str, account: str, message: str, msg: OutputMessage):
        channel = 'immchat'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))
    
    #imms see requests this way
    #[Whitechain (Goliath) Requests:] 'huehue'
    @action(r"^\[(\w+) (\(.*\)) Requests:] ('.*)'", color=False)
    def comms_request_other(self, speaker: str, account: str, message: str, msg:OutputMessage):
        channel = 'request'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    #only requesting player and imms can see
    @action(r"^(You) request, '(.*)'", color=False)
    def comms_request_self(self, speaker: str, message: str, msg: OutputMessage):
        channel = 'request'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    #imm only, all imms can see and listener can see
    @action(r"^\[(\w+) responds to (\w+) \((.*)\):] '(.*)'", color=False)
    def comms_respond(self, speaker: str, listener: str, listener_acct: str, msg:OutputMessage):
        channel = 'respond'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    @action(r"^The winds whisper, (.*)", color=False)
    def comms_world(self, message: str, msg: OutputMessage):
        channel = 'world'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    """
    Whitechain says, 'huehue'
    You say, 'huehue'
    """
    @action(r"^(\w+) say[s]?, '(.*)'", color=False)
    def comms_say(self, speaker: str, message: str, msg: OutputMessage):
        channel = 'say'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))

    #Vajra whispers to you, 'huehue'
    @action(r"(\w+) whispers to you, '(.*)'", color=False)
    def comms_whisper(self, speaker: str, message: str, msg: OutputMessage):
        listener = 'You'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message)) 

    """
    You tell Vajra (Anicca){Rp}, 'huehue'
    You tell Vajra{Rp}, 'huehue'
    """
    @action(r"You tell (.*){Rp}, '(.*)'", color=False)
    def comms_tell_self(self, listener: str, message: str, msg: OutputMessage):
        speaker = 'You'
        _listener = listener.split()
        if len(_listener) > 1:
            acct = _listener[1]
            acct = re.sub("\(|\)", '', acct)
            listener = _listener[0]
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))  

    """
    Vajra tells you, 'huehue'
    Whitechain (Goliath) tells you, 'huehue'
    """
    @action(r"^(.*) tells you, '(.*)'", color=False)
    def comms_tell_other(self, speaker: str, message: str, msg: OutputMessage):
        listener = 'You'
        _speaker = speaker.split()
        if len(_speaker) > 1:
            acct  = speaker[1]
            acct = re.sub("\(|\)", '', acct)
            speaker = _speaker[0]
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))  
    
    @action (r"^The winds whisper, '(.*)'", color=False)
    def comms_world(self, message: str, msg: OutputMessage):
        speaker = 'world'
        if self.comms_textlog is None:
            self.comms_textlog = self.session.screen.query_one("#commsTL", expect_type=TextLog)
        self.comms_textlog.write(Text.from_ansi(msg.message))