# Системка боя
class BattleSystem:
    def __init__(self, hero, enemies):
        if not isinstance(enemies, list):
            enemies = [enemies]
        self.hero = hero
        self.enemies = enemies

    def attack_enemy(self, index, damage=None):
        if damage is None:
            damage = self.hero.attack
        self.enemies[index].take_damage(damage)

    def enemy_attack(self, index):
        self.hero.take_damage(self.enemies[index].attack)

    def use_item(self, item, enemy_index=None):
        if item.effect == 'heal':
            self.hero.heal(item.value)
        elif item.effect == 'attack':
            if enemy_index is not None and self.enemies[enemy_index].hp > 0:
                self.enemies[enemy_index].take_damage(item.value)
            else:
                for i, e in enumerate(self.enemies):
                    if e.hp > 0:
                        e.take_damage(item.value)
                        break
        self.hero.inventory.remove(item)

    def is_over(self):
        return self.hero.hp <= 0 or all(e.hp <= 0 for e in self.enemies)

    def alive_indices(self):
        return [i for i, e in enumerate(self.enemies) if e.hp > 0]