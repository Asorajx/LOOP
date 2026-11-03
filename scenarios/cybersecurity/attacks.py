from abc import ABC, abstractmethod


class Attacker:
    def __init__(self, name):
        self.name = name

    def launch(self, attack, target):
        if not target.online:
            return False
        attack.execute(target)
        return True


class Attack(ABC):
    @abstractmethod
    def execute(self, target):
        pass


class MalwareAttack(Attack):
    def execute(self, target):
        target.infect()


class RansomwareAttack(MalwareAttack):
    def execute(self, target):
        super().execute(target)
        target.lock_files()


class InterceptAttack(Attack):
    def execute(self, target):
        target.intercept()
