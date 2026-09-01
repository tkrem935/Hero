# Настройка квестов
class Quest:
    def __init__(self, description, reward):
        self.description = description
        self.reward = reward
        self.completed = False

    def complete(self, hero):
        hero.add_item(self.reward)
        self.completed = True