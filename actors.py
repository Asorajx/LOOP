class Attacker:
    def __init__(self, name, attacks):
        self.__name = name
        self.__attacks = attacks
        self.__tracer = None

    @property
    def name(self):
        return self.__name

    @property
    def attacks(self):
        return self.__attacks

    def set_tracer(self, tracer):
        self.__tracer = tracer

        for attack in self.__attacks:
            attack.set_tracer(tracer)

    def perform_attack(self, attack, target):
        if hasattr(target, "device_id"):
            target_id = target.device_id
        else:
            target_id = target.connection_id

        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__name,
                "Attacker",
                "perform_attack",
                target_id
            )

        if target.blocked:
            if self.__tracer is not None:
                self.__tracer.method_completed(
                    self.__name,
                    "Attacker",
                    "perform_attack",
                    target_id,
                    message="Attack blocked"
                )

            return False

        attack.execute(target)

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__name,
                "Attacker",
                "perform_attack",
                target_id
            )

        return True

    def __str__(self):
        return f"Attacker: {self.__name}"


class Defender:
    def __init__(self, name):
        self.__name = name
        self.__tracer = None

    @property
    def name(self):
        return self.__name

    def set_tracer(self, tracer):
        self.__tracer = tracer

    def inspect(self, target):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__name,
                "Defender",
                "inspect",
                target.device_id
            )

        result = str(target)

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__name,
                "Defender",
                "inspect",
                target.device_id
            )

        return result

    def block(self, target):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__name,
                "Defender",
                "block",
                target.device_id
            )

        target.block()

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__name,
                "Defender",
                "block",
                target.device_id
            )

    def unblock(self, target):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__name,
                "Defender",
                "unblock",
                target.device_id
            )

        target.unblock()

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__name,
                "Defender",
                "unblock",
                target.device_id
            )

    def isolate(self, target):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__name,
                "Defender",
                "isolate",
                target.device_id
            )

        target.isolate()

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__name,
                "Defender",
                "isolate",
                target.device_id
            )

    def restore(self, target):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__name,
                "Defender",
                "restore",
                target.device_id
            )

        target.restore()

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__name,
                "Defender",
                "restore",
                target.device_id
            )

    def secure_connection(self, connection):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__name,
                "Defender",
                "secure_connection",
                connection.connection_id
            )

        connection.secure()

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__name,
                "Defender",
                "secure_connection",
                connection.connection_id
            )

    def __str__(self):
        return f"Defender: {self.__name}"