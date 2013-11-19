import rg

heatmap = None

class Heatmap:

    def __init__(self):
        self.turn = None
        self.map = {}

    def next(self, game, location):
        c_map = self._map(game)

        bx = location[0] - 1
        by = location[1] - 1

        max_heat = 0
        next_step = None
        for x in range(0, 2):
            tmp_x = bx + x
            if (tmp_x, by) in c_map and c_map[(tmp_x, by)] > max_heat:
                max_heat = c_map[(tmp_x, by)]
                next_step = (tmp_x, by)
            if (tmp_x, by + 2) in c_map and c_map[(tmp_x, by + 2)] > max_heat:
                max_heat = c_map[(tmp_x, by)]
                next_step = (tmp_x, by + 2)

        for y in range(0, 2):
            tmp_y = by + y
            if (bx, tmp_y) in c_map and c_map[(bx, tmp_y)] > max_heat:
                max_heat = c_map[(bx, tmp_y)]
                next_step = (bx + 2, tmp_y)
            if (bx + 2, tmp_y) in c_map and c_map[(bx + 2, tmp_y)] > max_heat:
                max_heat = c_map[(bx + 2, tmp_y)]
                next_step = (bx + 2, tmp_y)

        return next_step

    def _map(self, game):
        if game['turn'] == self.turn:
            return self.map

        self.map = {}
        for loc, enemy in game['robots'].iteritems():
            self._add_enemy(enemy)

        return self.map

    def _add(self, position, heat):
        if not position in self.map:
            self.map[position] = 0

        self.map[position] += heat

    def _add_enemy(self, enemy):
        center = enemy.location
        heat = enemy.hp

        self._add(center, heat)

        heat -= 10

        offset = 1
        bx = center[0] - offset
        by = center[1] - offset
        while heat > 0:
            for x in range(0, offset * 2):
                loc_types = rg.loc_types((bx + x, by))
                if not "invalid" in loc_types:
                    self._add((bx + x, by), heat)

                loc_types = rg.loc_types((bx + x, by + offset * 2))
                if not "invalid" in loc_types:
                    self._add((bx + x, by + offset * 2), heat)
            for y in range(0, offset * 2):
                loc_types = rg.loc_types((bx, by + y))
                if not "invalid" in loc_types:
                    self._add((bx, by + y), heat)

                loc_types = rg.loc_types((bx + offset * 2, by + y))
                if not "invalid" in loc_types:
                    self._add((bx + offset * 2, by + y), heat)

            heat -= 10


class Robot:

    def act(self, game):
        global heatmap

        if heatmap is None:
            heatmap = Heatmap()

        loc = heatmap.next(game, self.location)

        if loc is None:
            loc = rg.CENTER_POINT

        return ['move', loc]
