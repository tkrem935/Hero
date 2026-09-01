# Настройка злыдней
class Enemy:
    def __init__(self, name, hp, attack, xp=0):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.xp = xp

    def take_damage(self, dmg):
        self.hp -= dmg


class Boss(Enemy):
    def __init__(self, name, hp, attack, xp, special, special_name, special_chance=0.35):
        super().__init__(name, hp, attack, xp)
        self.special = special
        self.special_name = special_name
        self.special_chance = special_chance