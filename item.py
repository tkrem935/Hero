# Настройка айтемов
class Item:
    def __init__(self, name, effect, value):
        self.name = name
        self.effect = effect  # 'heal', 'attack' или 'buff'
        self.value = value