import rg


class Team:

    """All members in a team share one goal.
    ALL YOUR SQUADS ARE BELONG TO US!

    @type teams : list[Team]
    @type targets : dict[Robot, Team]
    """

    teams = []
    targets = []

    def __init__(self):
        Team.teams.append(self)
        self.teamsize = 2
        """:type : int"""
        self.members = []
        """:type : list[Robot]"""
        self.targets = {}
        """:type : dict[int, object]"""

    def target(self, bot, game):
        if game['turn'] != 0 and game['turn'] in self.targets:
            print "USE CACHED VALUED"
            return self.targets.get(game['turn'], rg.CENTER_POINT)

        min_dist = 1000
        target = None
        for loc, enemy in game['robots'].iteritems():
            if not bot in Team.targets and enemy.player_id != bot.player_id:
                dist = self._dist(enemy)
                if dist < min_dist:
                    min_dist = dist
                    target = enemy

        if target is None:
            return rg.CENTER_POINT

        Team.targets.append(target)

        self.targets[game['turn']] = target.location

        return target.location

    def _dist(self, enemy):
        """Calculates the lowest distance between the enemy and one of the team members.

        @type enemy: int
        """
        min_dist = 1000
        for bot in self.members:
            tmp_dist = rg.dist(enemy.location, bot.location)
            if tmp_dist < min_dist:
                min_dist = tmp_dist
        return min_dist

    def full(self):
        return len(self.members) >= 2


class Robot:

    def __init__(self):
        self.team = None
        """:type : Team | None"""
        self._assign_to_team()

    def act(self, game):
        """Uses group intelligence. Ask team what to do. All Robots in a team will return the same decision.

        @type self : Robot
        @type game : object
        """
        if not self.team is None:
            target = self.team.target(self, game)
            if rg.dist(self.location, target) == 1:
                return ['attack', target]
            elif rg.dist(self.location, target) == 2:
                # make blind attack
                gx = self.location[0] + (self.location[0] - target[0])
                gy = self.location[1] + (self.location[1] - target[1])
                return ['attack', (gx, gy)]
            else:
                return ['move', target]
        print "Fatal: Robot is not in team."

    def _get_closest_team(self):
        """Returns the team with a member closest to the given bot.

        @type self : Robot
        @rtype : Team
        """
        min_dist = 1000
        best_team = None
        for team in Team.teams:
            if not team.full():
                tmp_dist = team.get_closest_friend(self)
                if tmp_dist < min_dist:
                    min_dist = tmp_dist
                    best_team = team
        return best_team

    def _assign_to_team(self):
        """Assigns the robot to a team.

        @type self : Robot
        @rtype : None
        """
        best_team = self._get_closest_team()
        if best_team is None:
            best_team = Team()
        best_team.members.append(self)
        self.team = best_team