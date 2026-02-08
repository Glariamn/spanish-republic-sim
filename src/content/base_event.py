# src/content/base_event.py

class GameEvent:
    def __init__(self, state):
        self.state = state

    def should_trigger(self):
        """
        Prüft, ob das Event feuern soll. 
        Muss von den Kindern überschrieben werden.
        """
        return False

    def get_data(self):
        """
        Gibt das Dictionary zurück, das app.py erwartet.
        """
        raise NotImplementedError("Jedes Event muss seine Daten definieren.")