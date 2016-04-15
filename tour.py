from line import Line
from config import DISPLAY


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


    def intersections(self, all_clients):
        assert all_clients.__module__ == 'client', 'FATAL! all_clients seems not to be ClientsCollection'
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

        for it1 in range(len(lines)):
            line1 = lines[it1]
            for it2 in range(it1 + 1, len(lines)):
                line2 = lines[it2]
                crossing = line1.intersection_with(line2, all_clients)
                if DISPLAY['routing']['intersections']:
                    print('checking %s(%d) VS. %s(%d)' % (line1, it1, line2, it2))
                if crossing:
                    if DISPLAY['routing']['intersections']:
                        print('intersection:  %s  X  %s  @  %s' % (line1, line2, crossing))
                    intersect.append(crossing)

        return intersect
