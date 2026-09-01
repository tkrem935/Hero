import json
import os
import random
from hero import Hero
from enemy import Enemy, Boss
from item import Item
from battle import BattleSystem
from quest import Quest

SAVE_FILE = "save.json"

# ─────────────────────────────────────────
# Сохранение и загрузка
# ─────────────────────────────────────────

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hero = Hero(data["name"], hp=data["max_hp"], attack=data["attack"])
    hero.hp = data["hp"]
    hero.max_hp = data["max_hp"]
    hero.level = data["level"]
    hero.xp = data["xp"]
    hero.xp_to_next = data["xp_to_next"]
    hero.poisoned = data.get("poisoned", 0)
    hero.poison_damage = data.get("poison_damage", 0)
    hero.stunned = data.get("stunned", 0)
    for item_data in data["inventory"]:
        item = Item(item_data["name"], item_data["effect"], item_data["value"])
        hero.add_item(item)
    return hero, data.get("gold", 0)

def save_game(hero, gold):
    data = {
        "name": hero.name,
        "hp": hero.hp,
        "max_hp": hero.max_hp,
        "attack": hero.attack,
        "level": hero.level,
        "xp": hero.xp,
        "xp_to_next": hero.xp_to_next,
        "poisoned": hero.poisoned,
        "poison_damage": hero.poison_damage,
        "stunned": hero.stunned,
        "gold": gold,
        "inventory": [
            {"name": i.name, "effect": i.effect, "value": i.value}
            for i in hero.inventory
        ]
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────
# Справочники
# ─────────────────────────────────────────

MONSTERS = {
    "гоблин":  {"name": "Гоблин",  "hp": 15,  "attack": 4,  "xp": 20},
    "скелет":  {"name": "Скелет",  "hp": 40,  "attack": 8,  "xp": 35},
    "орк":     {"name": "Орк",     "hp": 60,  "attack": 10, "xp": 50},
    "дракон":  {"name": "Дракон",  "hp": 120, "attack": 18, "xp": 100},
}

SHOP_ITEMS = {
    "1": {"name": "Зелье лечения",   "effect": "heal",   "value": 30, "price": 10},
    "2": {"name": "Большое зелье",   "effect": "heal",   "value": 60, "price": 20},
    "3": {"name": "Бомба",           "effect": "attack", "value": 25, "price": 15},
    "4": {"name": "Острый меч",       "effect": "buff",   "value": 5,  "price": 30},
}

BOSSES = [
    Boss("Вождь Драконов", 150, 20, 200, "poison",        "Ядовитое дыхание"),
    Boss("Орк-Варвар",     180, 25, 200, "double_strike",  "Двойной удар"),
    Boss("Король Скелетов", 130, 22, 200, "stun",          "Парализующий взгляд"),
]

BOSS_REWARDS = {
    "Вождь Драконов":  Item("Драконья чешуя",    "heal",  80),
    "Орк-Варвар":      Item("Секира варвара",    "buff",  15),
    "Король Скелетов": Item("Корона проклятых", "heal", 100),
}

DUNGEON_FLOORS = [
    {
        "name": "1-й этаж: Вход",
        "choices": [
            {"desc": "Казармы (2 гоблина)", "type": "combat",
             "enemies": [("Гоблин", 15, 4, 20), ("Гоблин", 15, 4, 20)]},
            {"desc": "Тёмный туннель (событие)", "type": "event"},
        ]
    },
    {
        "name": "2-й этаж: Развилка",
        "choices": [
            {"desc": "Торговая палатка (магазин)", "type": "shop"},
            {"desc": "Святилище (полное лечение)", "type": "rest"},
        ]
    },
    {
        "name": "3-й этаж: Гарнизон",
        "choices": [
            {"desc": "Зал стражи (скелет + орк)", "type": "combat",
             "enemies": [("Скелет", 40, 8, 35), ("Орк", 60, 10, 50)]},
            {"desc": "Боковой проход (2 скелета)", "type": "combat",
             "enemies": [("Скелет", 40, 8, 35), ("Скелет", 40, 8, 35)]},
        ]
    },
    {
        "name": "4-й этаж: Преддверие",
        "choices": [
            {"desc": "Лагерь наёмников (магазин + лечение)", "type": "shop_rest"},
            {"desc": "Заброшенная комната (событие)", "type": "event"},
        ]
    },
    {
        "name": "5-й этаж: Тронный зал",
        "choices": [
            {"desc": "Сразиться с боссом", "type": "boss"},
        ]
    }
]

# ─────────────────────────────────────────
# Вывод
# ─────────────────────────────────────────

def print_header(title):
    print()
    print("=" * 52)
    print(f"  {title}")
    print("=" * 52)

def print_battle_status(hero, enemies, turn):
    print()
    print(f"  ── Ход {turn} ──")
    status = f"  {hero.name} [Ур.{hero.level}]:  HP {hero.hp}/{hero.max_hp}"
    if hero.poisoned > 0:
        status += f"  ☠ Отравлен ({hero.poisoned} ход.)"
    if hero.stunned > 0:
        status += f"  💫 Оглушён"
    print(status)
    for i, e in enumerate(enemies):
        tag = " [БОСС]" if isinstance(e, Boss) else ""
        hp_status = f"HP {e.hp}" if e.hp > 0 else "повержен"
        print(f"    {i+1}. {e.name}{tag} — {hp_status}")
        if isinstance(e, Boss) and e.hp > 0:
            print(f"       Способность: {e.special_name}")
    print()

def print_inventory(hero):
    if not hero.inventory:
        print("  Инвентарь пуст.")
        return
    for i, item in enumerate(hero.inventory, 1):
        print(f"  {i}. {item.name} ({item.effect}, +{item.value})")

def print_shop():
    print()
    print("  МАГАЗИН")
    print("  ─────────────────────────────────")
    for key, item in SHOP_ITEMS.items():
        print(f"  {key}. {item['name']:20s} {item['price']} зол.")
    print(f"  0. Выйти")

# ─────────────────────────────────────────
# Бой (несколько врагов + боссы)
# ─────────────────────────────────────────


def run_battle(hero, enemies_data, allow_flee=True):
    enemies = []
    total_xp = 0

    for ed in enemies_data:
        if isinstance(ed, Boss):
            # Босса оставляем как есть, чтобы сохранились special и т.д.
            enemies.append(ed)
            total_xp += ed.xp
        elif isinstance(ed, Enemy):
            # Обычного врага тоже оставляем
            enemies.append(ed)
            total_xp += ed.xp
        else:
            # Если пришёл кортеж (name, hp, attack, xp) — делаем обычного врага
            name, hp, atk, xp = ed
            enemy = Enemy(name, hp, atk, xp)
            enemies.append(enemy)
            total_xp += xp

    battle = BattleSystem(hero, enemies)
    turn = 1
    log = []

    names = ", ".join(e.name for e in enemies)
    print_header(f"БОЙ: {hero.name} против {names}")
    print_battle_status(hero, enemies, turn)


    while not battle.is_over():
        # ── Отравление ──
        if hero.poisoned > 0:
            hero.take_damage(hero.poison_damage)
            msg = f"[Ход {turn}] ☠ {hero.name} получает {hero.poison_damage} урона от яда"
            log.append(msg)
            print(f"  {msg}")
            hero.poisoned -= 1
            if hero.hp <= 0:
                break

        if battle.is_over():
            break

        # ── Оглушение ──
        if hero.stunned > 0:
            msg = f"[Ход {turn}] 💫 {hero.name} оглушён и пропускает ход!"
            log.append(msg)
            print(f"  {msg}")
            hero.stunned -= 1
        else:
            # ── Выбор действия ──
            alive = battle.alive_indices()
            print("  Действия:")
            print("    1. Атаковать")
            print("    2. Использовать предмет")
            if allow_flee:
                print("    3. Бежать")
            action = input("  > ").strip()

            # ── 1. Атаковать ──
            if action == "1":
                # Выбор цели
                if len(alive) == 1:
                    target_idx = alive[0]
                else:
                    print("  Выберите цель:")
                    for i in alive:
                        e = enemies[i]
                        tag = " [БОСС]" if isinstance(e, Boss) else ""
                        print(f"    {i+1}. {e.name}{tag} (HP {e.hp})")
                    choice = input("  > ").strip()
                    try:
                        target_idx = int(choice) - 1
                        if target_idx not in alive:
                            print("  Неверная цель.")
                            continue
                    except ValueError:
                        print("  Введите число.")
                        continue

                battle.attack_enemy(target_idx)
                target = enemies[target_idx]
                msg = f"[Ход {turn}] {hero.name} бьёт {target.name} на {hero.attack} урона"
                log.append(msg)
                print(f"  {msg}")
                if target.hp <= 0:
                    print(f"  💀 {target.name} повержен!")

            # ── 2. Предмет ──
            elif action == "2":
                if not hero.inventory:
                    print("  Инвентарь пуст!")
                    continue
                print("  Инвентарь:")
                print_inventory(hero)
                choice = input("  Номер предмета: ").strip()
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(hero.inventory):
                        item = hero.inventory[idx]
                        # Для атакующих предметов — выбор цели
                        target_idx = None
                        if item.effect == 'attack' and len(alive) > 1:
                            print("  Выберите цель:")
                            for i in alive:
                                e = enemies[i]
                                print(f"    {i+1}. {e.name} (HP {e.hp})")
                            tc = input("  > ").strip()
                            try:
                                target_idx = int(tc) - 1
                                if target_idx not in alive:
                                    print("  Неверная цель.")
                                    continue
                            except ValueError:
                                print("  Введите число.")
                                continue
                        battle.use_item(item, target_idx)
                        msg = f"[Ход {turn}] {hero.name} использует {item.name}"
                        log.append(msg)
                        print(f"  {msg}")
                    else:
                        print("  Неверный номер.")
                        continue
                except ValueError:
                    print("  Введите число.")
                    continue

            # ── 3. Бежать ──
            elif action == "3" and allow_flee:
                print("  Вы сбежали!")
                log.append(f"[Ход {turn}] {hero.name} сбежал")
                return "fled"

            else:
                print("  Неверная команда.")
                continue

        # ── Враги атакуют ──
        if battle.is_over():
            break

        for i in battle.alive_indices():
            enemy = enemies[i]

            # Проверка спецатаки босса
            used_special = False
            if isinstance(enemy, Boss) and random.random() < enemy.special_chance:
                if enemy.special == "poison":
                    hero.poisoned = 3
                    hero.poison_damage = 5
                    msg = f"[Ход {turn}] ☠ {enemy.name} использует «{enemy.special_name}»! {hero.name} отравлен на 3 хода."
                    log.append(msg)
                    print(f"  {msg}")
                    used_special = True
                elif enemy.special == "stun":
                    hero.stunned = 1
                    msg = f"[Ход {turn}] 💫 {enemy.name} использует «{enemy.special_name}»! {hero.name} оглушён."
                    log.append(msg)
                    print(f"  {msg}")
                    used_special = True
                elif enemy.special == "double_strike":
                    battle.enemy_attack(i)
                    battle.enemy_attack(i)
                    msg = f"[Ход {turn}] ⚔ {enemy.name} использует «{enemy.special_name}»! Двойной удар: {enemy.attack * 2} урона."
                    log.append(msg)
                    print(f"  {msg}")
                    used_special = True

            if not used_special:
                battle.enemy_attack(i)
                msg = f"[Ход {turn}] {enemy.name} бьёт {hero.name} на {enemy.attack} урона"
                log.append(msg)
                print(f"  {msg}")

            if hero.hp <= 0:
                break

        if battle.is_over():
            break

        turn += 1
        print_battle_status(hero, enemies, turn)

    # ── Итоги ──
    print_header("ЖУРНАЛ БОЯ")
    for entry in log:
        print(f"  {entry}")
    print()

    if hero.hp <= 0:
        print(f"  💀 {hero.name} пал в бою...")
        return "defeat"
    elif all(e.hp <= 0 for e in enemies):
        print(f"  ✅ {hero.name} победил!")
        hero.gain_xp(total_xp)
        return "victory"
    return "unknown"

# ─────────────────────────────────────────
# Магазин
# ─────────────────────────────────────────

def run_shop(hero, gold):
    print_header(f"МАГАЗИН | Золото: {gold}")
    print_shop()
    while True:
        choice = input("\n  Что купить? > ").strip()
        if choice == "0":
            print("  Вы вышли из магазина.")
            break
        if choice not in SHOP_ITEMS:
            print("  Нет такого товара.")
            continue
        item_data = SHOP_ITEMS[choice]
        if gold < item_data["price"]:
            print(f"  Не хватает золота! Нужно {item_data['price']}, у вас {gold}.")
            continue
        gold -= item_data["price"]
        print(f"  Куплено: {item_data['name']} за {item_data['price']} зол.")
        if item_data["effect"] == "buff":
            hero.attack += item_data["value"]
            print(f"  Атака +{item_data['value']}! Теперь: {hero.attack}")
        else:
            hero.add_item(Item(item_data["name"], item_data["effect"], item_data["value"]))
            print(f"  Предмет в инвентаре.")
        print(f"  Золота: {gold}")
    return gold

# ─────────────────────────────────────────
# Рандомные события
# ─────────────────────────────────────────

def random_event(hero, gold):
    events = [event_treasure, event_spring, event_trap, event_found_item,
              event_old_man, event_nothing]
    return random.choice(events)(hero, gold)

def event_treasure(hero, gold):
    found = random.randint(5, 25)
    gold += found
    print(f"  🎁 Сундук с сокровищами! +{found} золота (всего {gold}).")
    return gold

def event_spring(hero, gold):
    healed = min(30, hero.max_hp - hero.hp)
    hero.heal(healed)
    print(f"  ⛲ Целебный источник. +{healed} HP (теперь {hero.hp}/{hero.max_hp}).")
    return gold

def event_trap(hero, gold):
    dmg = random.randint(5, 15)
    hero.take_damage(dmg)
    print(f"  🪤 Ловушка! -{dmg} HP (теперь {hero.hp}/{hero.max_hp}).")
    return gold

def event_found_item(hero, gold):
    items = [Item("Ржавый кинжал", "attack", 10),
             Item("Найденное зелье", "heal", 25),
             Item("Странный свиток", "attack", 15)]
    item = random.choice(items)
    hero.add_item(item)
    print(f"  📦 Найден предмет: {item.name} ({item.effect}, +{item.value}).")
    return gold

def event_old_man(hero, gold):
    xp = random.randint(10, 30)
    print(f"  🧙 Старец делится мудростью: +{xp} XP")
    hero.gain_xp(xp)
    return gold

def event_nothing(hero, gold):
    print("  🌲 Тихая дорога. Ничего не произошло.")
    return gold

# ─────────────────────────────────────────
# Подземелье
# ─────────────────────────────────────────

def run_dungeon(hero, gold):
    print_header("ПОДЗЕМЕЛЬЕ")
    print("  Вы входите в тёмное подземелье...")
    print("  Пять этажов. На последнем — босс.")
    print()

    for floor_idx, floor in enumerate(DUNGEON_FLOORS):
        print_header(floor["name"])

        # Показ выбора
        choices = floor["choices"]
        for i, ch in enumerate(choices):
            print(f"  {i+1}. {ch['desc']}")

        if len(choices) > 1:
            pick = input("\n  Куда идём? > ").strip()
            try:
                pick_idx = int(pick) - 1
                if pick_idx < 0 or pick_idx >= len(choices):
                    pick_idx = 0
            except ValueError:
                pick_idx = 0
        else:
            pick_idx = 0
            input("\n  Нажмите Enter чтобы продолжить...")

        chosen = choices[pick_idx]

        # ── Выполнение ──
        if chosen["type"] == "combat":
            result = run_battle(hero, chosen["enemies"], allow_flee=True)
            if result == "victory":
                reward = random.randint(10, 25)
                gold += reward
                print(f"\n  +{reward} золота за зачистку.")
                heal = min(15, hero.max_hp - hero.hp)
                hero.heal(heal)
                print(f"  Восстановлено {heal} HP.")
            elif result == "fled":
                print("  Вы сбежали, но подземелье продолжается...")
            elif result == "defeat":
                print("\n  Вы пали в подземелье...")
                return "defeat", gold

        elif chosen["type"] == "event":
            print("\n  Что-то ждёт вас здесь...")
            gold = random_event(hero, gold)
            if hero.hp <= 0:
                print("\n  Герой погиб.")
                return "defeat", gold

        elif chosen["type"] == "shop":
            gold = run_shop(hero, gold)

        elif chosen["type"] == "rest":
            hero.hp = hero.max_hp
            hero.clear_status()
            print(f"  🏛 Святилище. HP восстановлено до {hero.max_hp}.")

        elif chosen["type"] == "shop_rest":
            gold = run_shop(hero, gold)
            hero.hp = hero.max_hp
            hero.clear_status()
            print(f"  🏕 Отдых в лагере. HP: {hero.hp}/{hero.max_hp}.")

        elif chosen["type"] == "boss":
            # Выбираем босса как объект, не делаем кортежи
            boss = random.choice(BOSSES)

            print()
            print("  ╔══════════════════════════════════════╗")
            print(f"  ║  БОСС: {boss.name}")
            print(f"  ║  HP: {boss.hp}  Атака: {boss.attack}")
            print(f"  ║  Способность: {boss.special_name}")
            print("  ╚══════════════════════════════════════╝")
            print()

            # Передаём список с объектом Boss, без конвертации в кортежи
            result = run_battle(hero, [boss], allow_flee=False)

            if result == "victory":
                reward_item = BOSS_REWARDS[boss.name]
                hero.add_item(reward_item)
                boss_gold = 100
                gold += boss_gold
                print(f"\n  🏆 БОСС ПОВЕРЖЕН!")
                print(f"  Награда: {reward_item.name} + {boss_gold} золота")
                print(f"  Подземелье пройдено!")
                return "dungeon_complete", gold
            elif result == "defeat":
                print("\n  Босс оказался слишком силён...")
                return "defeat", gold
    return "dungeon_complete", gold

# ─────────────────────────────────────────
# Создание врага (обычный бой)
# ─────────────────────────────────────────

def create_enemy():
    print("\n  Враг: Гоблин / Скелет / Орк / Дракон")
    choice = input("  > ").strip().lower()
    if choice not in MONSTERS:
        print("  Неизвестный, ставим «Скелет».")
        choice = "скелет"
    d = MONSTERS[choice]
    return Enemy(d["name"], d["hp"], d["attack"], d["xp"]), d["xp"]

# ─────────────────────────────────────────
# Главная функция
# ─────────────────────────────────────────

def main():
    print_header("RPG-БАТТЛ: ПРОТОТИП ИНДИ-ИГРЫ")
    print("  Версия: 0.4.0")
    print("  Новое: боссы, несколько врагов, подземелье")

    # ── Загрузка ──
    hero = None
    gold = 20
    saved = load_game()
    if saved:
        saved_hero, saved_gold = saved
        print("\n  Найдено сохранение. Загрузить? (да/нет)")
        if input("  > ").strip().lower() == "да":
            hero = saved_hero
            gold = saved_gold
            print(f"  Загружен: {hero.name} [Ур.{hero.level}]")
            print(f"  HP: {hero.hp}/{hero.max_hp} | Атк: {hero.attack} | Золото: {gold}")

    if not hero:
        print("\n  Имя героя:")
        name = input("  > ").strip() or "Герой"
        hero = Hero(name, hp=100, attack=15)
        hero.add_item(Item("Зелье лечения", "heal", 30))
        print(f"  Создан: {hero.name}, HP=100, Атака=15")

    # ── Игровой цикл ──
    while True:
        print_header("ГЛАВНОЕ МЕНЮ")
        print(f"  {hero.name} [Ур.{hero.level}]")
        print(f"  HP: {hero.hp}/{hero.max_hp} | Атк: {hero.attack} | Золото: {gold}")
        print(f"  XP: {hero.xp}/{hero.xp_to_next}")
        print()
        print("  1. В бой")
        print("  2. Магазин")
        print("  3. Инвентарь")
        print("  4. Исследовать окрестности")
        print("  5. Подземелье (5 этажей + босс)")
        print("  6. Сохранить и выйти")

        choice = input("  > ").strip()

        # ── 1. В бой ──
        if choice == "1":
            enemy, enemy_xp = create_enemy()
            result = run_battle(hero, [enemy], allow_flee=True)
            if result == "victory":
                reward = random.randint(10, 25)
                gold += reward
                print(f"\n  +{reward} золота.")
                heal = min(20, hero.max_hp - hero.hp)
                hero.heal(heal)
                print(f"  +{heal} HP после боя.")
            elif result == "defeat":
                print("\n  Игра окончена.")
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                break

        # ── 2. Магазин ──
        elif choice == "2":
            gold = run_shop(hero, gold)

        # ── 3. Инвентарь ──
        elif choice == "3":
            print_header("ИНВЕНТАРЬ")
            print(f"  {hero.name} [Ур.{hero.level}]")
            print(f"  HP: {hero.hp}/{hero.max_hp} | Атк: {hero.attack} | Золото: {gold}")
            print(f"  XP: {hero.xp}/{hero.xp_to_next}")
            if hero.poisoned > 0:
                print(f"  ☠ Отравлен ({hero.poisoned} ход.)")
            if hero.stunned > 0:
                print(f"  💫 Оглушён")
            print()
            print_inventory(hero)

        # ── 4. Исследование ──
        elif choice == "4":
            print_header("ИССЛЕДОВАНИЕ")
            gold = random_event(hero, gold)
            if hero.hp <= 0:
                print("\n  Герой погиб.")
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                break
            if random.random() < 0.3:
                print("\n  Ещё что-то...")
                gold = random_event(hero, gold)
                if hero.hp <= 0:
                    print("\n  Герой погиб.")
                    if os.path.exists(SAVE_FILE):
                        os.remove(SAVE_FILE)
                    break

        # ── 5. Подземелье ──
        elif choice == "5":
            result, gold = run_dungeon(hero, gold)
            if result == "defeat":
                print("\n  Подземелье не пройдено.")
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                print("  Игра окончена.")
                break
            elif result == "dungeon_complete":
                print("\n  Вы вернулись из подземелья с добычей!")

        # ── 6. Сохранить ──
        elif choice == "6":
            save_game(hero, gold)
            print("\n  Сохранено. До встречи!")
            break

        else:
            print("  Введите 1–6.")

if __name__ == "__main__":
    main()
