class DiscordHandler:
    # each guild has one canvas handler
    def __init__(self):
        self._canvas_handlers = []
        self._guilds = []

    @property
    def canvas_handlers(self):
        return self._canvas_handlers
    
    @canvas_handlers.setter
    def canvas_handlers(self, canvas_handlers):
        self._canvas_handlers = canvas_handlers
    
    @property
    def guilds(self):
        return self._guilds
    
    @guilds.setter
    def guilds(self, guilds):
        self._guilds = guilds