from line import Line


class Tour():
    def __init__(self, clients, plan=None):
        self.clients = clients
        self.plan = []
        self.final_length = 0.0

        if plan:
            self.plan = plan


    def __lt__(self, other):
        return self.length() < other.length()


    def length(self):
        tour_length = 0.0
        last = None
        for tcli in self.plan:
            if last is None:
                last = tcli
            else:
                tour_length += tcli.distance_to(last)
                last = tcli

        if not self.final_length and len(self.plan) == len(self.clients):
            self.final_length = tour_length

        return tour_length


    def assign(self, next_client):
        self.plan.append(next_client)


    def get_last_assigned(self):
        if not len(self.plan):
            return None
        else:
            return self.plan[-1]


    def is_incomplete(self):
        return True if len(self.plan) < len(self.clients) else False


    def intersections(self):
        lines = []
        intersect = []

        if len(self.plan) < 2:
            return None

        origin = self.plan[0]

        for end in self.plan:
            if end == self.plan[0]:
                continue

            new_line = Line(origin, end)
            lines.append(new_line)
            origin = end

        for line1 in lines:
            for line2 in lines:
                if line1 == line2:
                    continue

                crossing = line1.intersection_with(line2)
                if crossing:
                    print('%s  X  %s  @  %s' % (line1, line2, crossing))
                    intersect.append(crossing)

        print('%d intersections' % len(intersect))
        return intersect
