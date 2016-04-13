from client import Client


class Line():
    def __init__(self, client1, client2):
        self.origin = client1       # x1/y1
        self.end = client2          # x2/y2
        self.slope = None           # m
        self.addition = None        # n
                                    # f(x) = m * x + n

    def __repr__(self):
        return '%s -> %s' % (self.origin, self.end)


    def __eq__(self, other):
        return False if other is None else (self.origin == other.origin and self.end == other.end)


    def get_slope(self):
        if not self.slope:
            self.slope = (self.end.y - self.origin.y)/(self.end.x - self.origin.x)

        return self.slope


    def get_addition(self):
        if not self.addition:
            self.addition = self.origin.y - self.get_slope() * self.origin.x

        return self.addition


    def intersection_with(self, other_line):
        if self.get_slope() == other_line.get_slope():
            return None

        int_x = (other_line.get_addition() - self.get_addition()) / (self.get_slope() - other_line.get_slope())
        int_y = self.slope * int_x + self.addition

        return Client(int_x, int_y) 


