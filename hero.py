# Настройка героя
class Hero:
    def __init__(self, name, hp=100, attack=10):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.inventory = []
        self.level = 1
        self.xp = 0
        self.xp_to_next = 50

        # Статус-эффекты
        self.poisoned = 0          # сколько ходов осталось отравления
        self.poison_damage = 0    # урон за ход от яда
        self.stunned = 0           # сколько ходов оглушения

    def take_damage(self, dmg):
        self.hp -= dmg

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def add_item(self, item):
        self.inventory.append(item)

    def gain_xp(self, amount):
        self.xp += amount
        print(f"  +{amount} XP (всего: {self.xp}/{self.xp_to_next})")
        while self.xp >= self.xp_to_next:
            self.level_up()

    def level_up(self):
        self.xp -= self.xp_to_next
        self.level += 1
        self.xp_to_next = int(self.xp_to_next * 1.5)
        self.max_hp += 20
        self.attack += 5
        self.hp = self.max_hp
        print()
        print("  ╔══════════════════════════════════╗")
        print(f"  ║  LEVEL UP! Теперь уровень {self.level:<5}   ║")
        print(f"  ║  Max HP: {self.max_hp:<5}  Атака: {self.attack:<5}   ║")
        print("  ╚══════════════════════════════════╝")
        print()

    def clear_status(self):
        self.poisoned = 0
        self.poison_damage = 0
        self.stunned = 0