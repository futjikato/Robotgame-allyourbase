import rg

heatmap = None


class Heatmap:

    def __init__(self):
        self.turn = None
        self.map = {}
        self.old_map = {}
        self.enemy_positions = {}

    def is_enemy_position(self, loc):
        return loc in self.enemy_positions

    def get_enemy(self, loc):
        if self.is_enemy_position(loc):
            return self.enemy_positions[loc]

    def next(self, game, cbot):
        location = cbot.location
        c_map = self._map(game, cbot)

        # self._pretty_print(repr(game['turn']))

        next_step = (location[0] - 1, location[1])
        if next_step in c_map:
            min_steps = c_map[next_step]
        else:
            min_steps = 1000
            next_step = rg.CENTER_POINT

        tmp_step = (location[0] + 1, location[1])
        if tmp_step in c_map and c_map[tmp_step] < min_steps:
            min_steps = c_map[tmp_step]
            next_step = tmp_step

        tmp_step = (location[0], location[1] - 1)
        if tmp_step in c_map and c_map[tmp_step] < min_steps:
            min_steps = c_map[tmp_step]
            next_step = tmp_step

        tmp_step = (location[0], location[1] + 1)
        if tmp_step in c_map and c_map[tmp_step] < min_steps:
            min_steps = c_map[tmp_step]
            next_step = tmp_step

        last_dist = 50
        if next_step in self.old_map:
            last_dist = self.old_map[next_step]

        return next_step, min_steps, last_dist

    def _map(self, game, bot):
        if game['turn'] == self.turn:
            return self.map

        self.old_map = self.map
        self.map = {}
        self.turn = game['turn']
        self.enemy_positions = {}
        for loc, other in game['robots'].iteritems():
            if other.player_id != bot.player_id:
                self._add_enemy(other)
            else:
                self._add_fiend(other)

        return self.map

    def _pretty_print(self, iteration):
        f = open('map-turn' + iteration + ".txt", 'w')
        mapout = ""

        for i in range(0, rg.CENTER_POINT[0] * 2):
            for j in range(0, rg.CENTER_POINT[1] * 2):
                loc = (i, j)

                warn = " "
                if loc in self.enemy_positions:
                    warn = "x"

                if not loc in self.map:
                    self.map[loc] = 1000

                mapout += "%s[%s]=%s " % (repr(loc).rjust(8), warn, repr(self.map[loc]).ljust(5))
            mapout += '\n'

        f.write(mapout)
        f.close()

    def _add(self, position, wdist):
        if position[0] < 0 or position[1] < 0:
            return

        loc_types = rg.loc_types(position)
        if "invalid" in loc_types or "obstacle" in loc_types:
            return

        if not position in self.map or self.map[position] > wdist:
            self.map[position] = wdist

    def _add_enemy(self, enemy):
        center = enemy.location

        self.enemy_positions[center] = enemy
        self._add(center, 0)

        offset = 1
        while offset < rg.CENTER_POINT[0]:
            bx = center[0] - offset
            by = center[1] - offset
            radius = offset * 2

            self._add((bx, by), rg.wdist(center, (bx, by)))
            for x in range(1, radius + 1):
                self._add((bx + x, by), rg.wdist(center, (bx + x, by)))
                self._add((bx + x, by + (offset * 2)), rg.wdist(center, (bx + x, by + (offset * 2))))

            for y in range(1, radius + 1):
                self._add((bx, by + y), rg.wdist(center, (bx, by + y)))
                self._add((bx + (offset * 2), by + y), rg.wdist(center, (bx + (offset * 2), by + y)))

            offset += 1

    def _add_fiend(self, bot):
        self.map[bot.location] = 1000
        for loc in rg.locs_around(bot.location):
            if "spawn" in rg.loc_types(loc):
                self.map[loc] = 500


class Robot:

    def act(self, game):
        global heatmap

        if heatmap is None:
            heatmap = Heatmap()

        data = heatmap.next(game, self)
        loc = data[0]
        wdist = data[1]
        old_wdist = data[2]

        # something is coming get ready for collision
        if wdist == 1 and old_wdist > wdist:
            return ['guard']

        if loc is None:
            loc = rg.toward(self.location, rg.CENTER_POINT)

        min_hp = 100
        target = None
        target_count = 0
        for aloc in rg.locs_around(self.location):
            if heatmap.is_enemy_position(aloc):
                target_count += 1
                c_target = heatmap.get_enemy(aloc)
                if c_target.hp < min_hp:
                    min_hp = c_target.hp
                    target = c_target

        if target_count > 1 and self.hp < 20:
            return ['suicide']

        if target_count == 1 and self.hp < 10:
            return ['suicide']

        if not target is None:
            return ['attack', target.location]

        return ['move', loc]