import rg

class Robot:

    def __init__(self):
        self.history = []
        self.backupThreshold = 50

    def act(self, game):
        # check if we need to back up a little to save robot
        if self.hp < self.backupThreshold and len(self.history) > 0:
            print "BACKUP"
            return ['move', self.history.pop()]

        # find closest enemy robot
        minDist = 1000
        target = None
        for loc, bot in game['robots'].iteritems():
            if bot.player_id != self.player_id:
                checkDist = rg.dist(loc, self.location)
                if checkDist < minDist:
                    minDist = checkDist
                    target = loc

        # if mindist is 2 try to guess attack enemy position
        if minDist == 2:
            gx = self.location[0] + self.location[0] - target[0]
            gy = self.location[0] + self.location[1] - target[1]

            return ['attack', (gx, gy)]

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