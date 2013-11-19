import rg

class Robot:

    def __init__(self):
        self.history = []
        self.backupThreshold = 50

    def act(self, game):
        # check if we need to back up a little to save robot
        if self.hp < self.backupThreshold and len(self.history) > 0:
            back_location = rg.toward(self.location, self.history.pop())
            if back_location != self.location:
                return ['move', back_location]

        # find closest enemy robot
        minDist = 1000
        target = None
        for loc, bot in game['robots'].iteritems():
            if bot.player_id != self.player_id:
                checkDist = rg.dist(loc, self.location)
                if checkDist < minDist:
                    minDist = checkDist
                    target = loc

        # HOIST THE FLAG! ARM THE CANONS!
        if minDist == 1:
            return ['attack', target]

        if target is None:
            target = rg.CENTER_POINT

        # calculate target location
        newlocation = rg.toward(self.location, target)
        self.history.append(newlocation)

        # move
        return ['move', newlocation]