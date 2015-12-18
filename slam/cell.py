import math

class Cell:
    def __init__(self, occupation=None):
        """
        self.occupied is a value between 0 (free) and 100 (occupied) if it's occupancy is known,
            else None.
            It's a percentage indicates how sure we are about something is there.
        self.occupied is a log-odds value (from -inf to inf), where
           0 means unknown,
           -inf means certainly free,
           and inf means certainly occupied.
        """
        self.occupation = occupation
        self.occupied = 0
        self.hasRobot = False

    def add_log_odds(self, delta):
        self.set_log_odds(self.occupied + delta)

    def set_log_odds(self, occupied):
        self.occupied = occupied
        if (-500 < occupied < 500):
            self._set(1 - 1/(1 + math.exp(occupied)))
        else:
            self._set(1 if occupied > 0 else 0)

    def _set(self, occupation):
        if(occupation is None):
            self.occupation = None
            return
        if(isinstance(occupation, bool)):
            occupation = 1 if occupation else 0

        assert (0 <= occupation <= 1), ("Invalid occupation range, expected value between 0 and 100, got "+str(occupation))
        self.occupation = occupation

    def get_log_odds(self):
        return self.occupied

    def get(self):
        return self.occupation



    def __str__(self):
        if self.hasRobot:
            return self.hasRobot
        if self.occupation is None:
           return '░'
        chars = " ▁▂▃▄▅▆▇█"
        i = int(self.occupation * (len(chars)-1))
        return chars[i]


    def origin_str(self):
        if self.hasRobot:
            return self.hasRobot
        if self.occupation is None:
            return '◌'
        chars = "○◎◍◒◕●◙"
        i = int(self.occupation * (len(chars)-1))
        return chars[i]
        return str(self.occupation)


    def __repr__(self):
        if (self.occupation is None):
            return "Cell()"

        return "Cell("+repr(self.occupation)+")"
