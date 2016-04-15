from client import Client


class Line():
    def __init__(self, client1, client2):
        self.origin = client1       # x1/y1
        self.end = client2          # x2/y2
        self.slope = None           # m
        self.addition = None        # n
                                    # f(x) = m * x + n
        self.calculate_and_verify()


    def __repr__(self):
        return '%s -> %s' % (self.origin, self.end)


    def __eq__(self, other):
        return False if other is None else (self.origin == other.origin and self.end == other.end)


    def get_slope(self):
        if not self.slope:
            self.slope = (self.end.y - self.origin.y)/float(self.end.x - self.origin.x)

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
        intersect_coords = Client(int(int_x), int(int_y))

        if within_line_boundary(self, intersect_coords) and within_line_boundary(other_line, intersect_coords):
            return intersect_coords
        else:
            return None


    def calculate_and_verify(self):
        m_val = self.get_slope()
        n_val = self.get_addition()

        y_val = m_val * self.origin.x + n_val
        assert y_val >= self.origin.y - 1 and y_val <= self.origin.y + 1, 'calculations incorrect for y: %d != %d' % (self.origin.y, y_val)
        y_val = m_val * self.end.x + n_val
        assert y_val >= self.end.y - 1 and y_val <= self.end.y + 1, 'calculations incorrect for y: %d != %d' % (self.end.y, y_val)


def within_line_boundary(line, coords):
    x_min = line.origin.x if line.origin.x < line.end.x else line.end.x
    x_max = line.origin.x if line.origin.x > line.end.x else line.end.x
    y_min = line.origin.y if line.origin.y < line.end.y else line.end.y
    y_max = line.origin.y if line.origin.y > line.end.y else line.end.y

    if coords == line.end or coords == line.origin:
        return False

    return True if x_min <= coords.x <= x_max and y_min <= coords.y <= y_max else False


