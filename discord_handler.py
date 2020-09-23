class DiscordHandler:
    # each guild has one canvas handler
    def __init__(self):
        # TODO: remove self._guilds and instead have [ch[0] for ch in self.canvas_handlers]
        self._canvas_handlers = []   # [c_handler1, ... ]

    @property
    def canvas_handlers(self):
        return self._canvas_handlers
    
    @canvas_handlers.setter
    def canvas_handlers(self, canvas_handlers):
        self._canvas_handlers = canvas_handlers