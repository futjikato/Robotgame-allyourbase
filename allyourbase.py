import rg


class Robot:

    def act(self, game):
        # find closest enemy robot
        min_dist = 1000
        target = None
        for loc, bot in game['robots'].iteritems():
            if bot.player_id != self.player_id:
                check_dist = rg.wdist(loc, self.location)
                if check_dist < min_dist:
                    min_dist = check_dist
                    target = loc

        # HOIST THE FLAG! ARM THE CANONS!
        if min_dist == 1:
            return ['attack', target]

        if target is None:
            target = rg.CENTER_POINT

        # calculate target location
        newlocation = rg.toward(self.location, target)

        # move
        return ['move', newlocation]