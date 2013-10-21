class ClientState:
    UNASSOCIATED = 1
    ASSOCIATED   = 2


class Client:
    def __init__(self, state=ClientState.UNASSOCIATED, x=0, y=0):
        self.x = x
        self.y = y
        self.state = state

