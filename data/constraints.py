import data.meta_types


class Constraint:

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.priority = -1

    def __str__(self):
        return "{0} ? {1}".format(self.left, self.right)

    def __repr__(self):
        return self.__str__()


class Sub(Constraint):

    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 10

    def __str__(self):
        return "{0} : {1}".format(self.left, self.right)


class Eq(Constraint):

    def __init__(self, left, right):
        Constraint.__init__(self, left, right)
        self.priority = 1

    def __str__(self):
        return "{0} = {1}".format(self.left, self.right)
