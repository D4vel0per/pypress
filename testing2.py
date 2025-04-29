from testing import Home

class House (Home):
    def __init__(self):
        Home.turn_on = self.turn_on
    def turn_on(mode):
        print("TURNING ON THE LIGHTS ON THE HOUSEEE")