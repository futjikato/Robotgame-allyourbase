import rg
import random


class Fortress:
    def __init__(self, player_id, game):
        self.enemy_list = []
        self.friend_list = []
        self.occupied = []
        for loc, bot in game['robots'].iteritems():
            self.occupied.append(bot.location)
            if bot.player_id != player_id:
                self.enemy_list.append(bot)
            else:
                self.friend_list.append(bot)

    def next(self, bot):
        bad_steps = []
        watch_out = []
        attack_steps = []
        rest_steps = []
        better_steps = []
        should_move = False
        around = rg.locs_around(bot.location, ["invalid", "obstacle"])
        for loc in around:
            if "spawn" in rg.loc_types(loc):
                bad_steps.append(loc)
                should_move = True
            else:
                set = False
                for other in self.enemy_list:
                    if other.location == loc:
                        attack_steps.append(loc)
                        set = True

                    if other.location in rg.locs_around(loc):
                        watch_out.append(loc)
                        set = True

                for other in self.friend_list:
                    if other.location == loc:
                        bad_steps.append(loc)
                        set = True
                        should_move = True

                    if other.location in rg.locs_around(loc):
                        olx = other.location[0]
                        oly = other.location[1]
                        tests = [(olx + 1, oly + 1), (olx + 1, oly - 1), (olx - 1, oly + 1), (olx - 1, oly - 1)]
                        min_wd = 10
                        final = None

                        for check in tests:
                            wd = rg.wdist(bot.location, check)
                            check_types = rg.loc_types(check)
                            if wd < min_wd and not "obstacle" in check_types and not "invalid" in check_types and not check in self.occupied:
                                min_wd = wd
                                final = check

                        if not final is None:
                            better_steps.append(rg.toward(bot.location, final))
                            set = True

                if not set:
                    rest_steps.append(loc)

        if len(attack_steps) > 1 and len(rest_steps) > 0:
            if bot.hp <= 16:
                return ['suicide']
            return ['move', rest_steps.pop()]

        if len(attack_steps) > 1 and len(rest_steps) == 0:
            if bot.hp <= 16:
                return ['suicide']
            else:
                return ['attack', attack_steps.pop()]

        if len(attack_steps) == 1:
            if bot.hp < 9:
                return ['suicide']
            else:
                return ['attack', attack_steps.pop()]

        if should_move and len(rest_steps) > 0:
            index = 0
            if len(rest_steps) > 1:
                index = random.randrange(0, (len(rest_steps) - 1))

            return ['move', rest_steps.pop(index)]

        if len(better_steps) > 0:
            return ['move', better_steps.pop()]

        return ['guard']


fortress = None
turn = None


class Robot:
    def __init__(self):
        self.target = None

    def act(self, game):
        global turn
        global fortress

        # initialize fortress
        # renew fortress every new turn
        if game['turn'] != turn:
            fortress = Fortress(self.player_id, game)

        return fortress.next(self)