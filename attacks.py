from abc import ABC, abstractmethod


class Attack(ABC):
    def __init__(self, name):
        self.__name = name
        self.__tracer = None

    @property
    def name(self):
        return self.__name

    @property
    def tracer(self):
        return self.__tracer

    def set_tracer(self, tracer):
        self.__tracer = tracer

    @abstractmethod
    def execute(self, target):
        pass

    def __str__(self):
        return f"Attack: {self.__name}"


class CredentialAttack(Attack):
    def __init__(self):
        super().__init__("Credential Attack")

    def execute(self, target):
        if self.tracer is not None:
            self.tracer.method_started(
                self.name,
                "CredentialAttack",
                "execute",
                target.device_id
            )

        target.increase_risk(1)

        if self.tracer is not None:
            self.tracer.method_completed(
                self.name,
                "CredentialAttack",
                "execute",
                target.device_id
            )


class MitMAttack(Attack):
    def __init__(self):
        super().__init__("MITM Attack")

    def execute(self, target):
        if self.tracer is not None:
            self.tracer.method_started(
                self.name,
                "MitMAttack",
                "execute",
                target.connection_id
            )

        target.intercept()

        if self.tracer is not None:
            self.tracer.method_completed(
                self.name,
                "MitMAttack",
                "execute",
                target.connection_id
            )


class DoSAttack(Attack):
    def __init__(self, name="DoS Attack"):
        super().__init__(name)

    def execute(self, target):
        if self.tracer is not None:
            self.tracer.method_started(
                self.name,
                "DoSAttack",
                "execute",
                target.device_id
            )

        target.increase_risk(1)
        target.overload("HIGH")

        if self.tracer is not None:
            self.tracer.method_completed(
                self.name,
                "DoSAttack",
                "execute",
                target.device_id
            )


class DDoSAttack(DoSAttack):
    def __init__(self):
        super().__init__("DDoS Attack")

    def execute(self, target):
        if self.tracer is not None:
            self.tracer.method_started(
                self.name,
                "DDoSAttack",
                "execute",
                target.device_id
            )

        super().execute(target)
        target.increase_risk(1)
        target.overload("CRITICAL")

        if self.tracer is not None:
            self.tracer.method_completed(
                self.name,
                "DDoSAttack",
                "execute",
                target.device_id
            )


class MalwareAttack(Attack):
    def __init__(self, name="Malware Attack"):
        super().__init__(name)

    def execute(self, target):
        if self.tracer is not None:
            self.tracer.method_started(
                self.name,
                "MalwareAttack",
                "execute",
                target.device_id
            )

        target.increase_risk(2)

        if self.tracer is not None:
            self.tracer.method_completed(
                self.name,
                "MalwareAttack",
                "execute",
                target.device_id
            )


class RansomwareAttack(MalwareAttack):
    def __init__(self):
        super().__init__("Ransomware Attack")

    def execute(self, target):
        if self.tracer is not None:
            self.tracer.method_started(
                self.name,
                "RansomwareAttack",
                "execute",
                target.device_id
            )

        super().execute(target)
        target.increase_risk(1)
        target.lock_files()

        if self.tracer is not None:
            self.tracer.method_completed(
                self.name,
                "RansomwareAttack",
                "execute",
                target.device_id
            )