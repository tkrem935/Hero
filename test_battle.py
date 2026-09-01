from hero import Hero
from enemy import Enemy, Boss
from item import Item
from battle import BattleSystem

def test_battle():
    hero = Hero("Герой")
    enemy = Enemy("Скелет", 20, 5, 35)
    battle = BattleSystem(hero, enemy)
    battle.attack_enemy(0)
    assert enemy.hp == 10, f"Ожидалось 10, получили {enemy.hp}"
    battle.enemy_attack(0)
    assert hero.hp == 95, f"Ожидалось 95, получили {hero.hp}"
    print("✅ test_battle: пройден")

def test_multi_enemy():
    hero = Hero("Герой", hp=100, attack=20)
    e1 = Enemy("Гоблин", 15, 4, 20)
    e2 = Enemy("Орк", 60, 10, 50)
    battle = BattleSystem(hero, [e1, e2])
    assert len(battle.enemies) == 2
    assert battle.alive_indices() == [0, 1]
    battle.attack_enemy(0)
    assert e1.hp <= 0
    assert battle.alive_indices() == [1]
    assert not battle.is_over()
    battle.attack_enemy(1)
    battle.attack_enemy(1)
    battle.attack_enemy(1)
    assert e2.hp <= 0
    assert battle.is_over()
    print("✅ test_multi_enemy: пройден")

def test_leveling():
    hero = Hero("Герой")
    assert hero.level == 1
    hero.gain_xp(50)
    assert hero.level == 2
    assert hero.max_hp == 120
    assert hero.attack == 20
    assert hero.xp_to_next == 75
    print("✅ test_leveling: пройден")

def test_heal_cap():
    hero = Hero("Т", hp=100, attack=10)
    hero.take_damage(10)
    hero.heal(999)
    assert hero.hp == 100
    print("✅ test_heal_cap: пройден")

def test_poison():
    hero = Hero("Т", hp=100, attack=10)
    hero.poisoned = 3
    hero.poison_damage = 5
    assert hero.poisoned == 3
    hero.take_damage(hero.poison_damage)
    hero.poisoned -= 1
    assert hero.hp == 95
    assert hero.poisoned == 2
    print("✅ test_poison: пройден")

def test_stun():
    hero = Hero("Т", hp=100, attack=10)
    hero.stunned = 1
    assert hero.stunned == 1
    hero.stunned -= 1
    assert hero.stunned == 0
    print("✅ test_stun: пройден")

def test_boss():
    boss = Boss("Тест-Босс", 100, 15, 200, "poison", "Яд", 0.5)
    assert boss.special == "poison"
    assert boss.special_name == "Яд"
    assert boss.special_chance == 0.5
    assert boss.hp == 100
    assert isinstance(boss, Enemy)
    print("✅ test_boss: пройден")

def test_save_load():
    import json, os
    hero = Hero("Тест", hp=100, attack=15)
    hero.add_item(Item("Зелье", "heal", 30))
    hero.take_damage(20)
    hero.poisoned = 2
    data = {
        "name": hero.name, "hp": hero.hp, "max_hp": hero.max_hp,
        "attack": hero.attack, "level": hero.level,
        "xp": hero.xp, "xp_to_next": hero.xp_to_next,
        "poisoned": hero.poisoned, "poison_damage": hero.poison_damage,
        "stunned": hero.stunned, "gold": 50,
        "inventory": [{"name": i.name, "effect": i.effect, "value": i.value} for i in hero.inventory]
    }
    with open("test_save.json", "w", encoding="utf-8") as f:
        json.dump(data, f)
    with open("test_save.json", "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["hp"] == 80
    assert loaded["poisoned"] == 2
    os.remove("test_save.json")
    print("✅ test_save_load: пройден")

if __name__ == "__main__":
    test_battle()
    test_multi_enemy()
    test_leveling()
    test_heal_cap()
    test_poison()
    test_stun()
    test_boss()
    test_save_load()
    print("\n🎉 Все тесты пройдены!")
