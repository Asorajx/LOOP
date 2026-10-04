from tracing import ExecutionTracer


class CyberDefenseSimulation:
    def __init__(self, attacker, defender, devices, connections):
        self.__attacker = attacker
        self.__defender = defender
        self.__devices = devices
        self.__connections = connections
        self.__tracer = ExecutionTracer()

        self.__attacker.set_tracer(self.__tracer)
        self.__defender.set_tracer(self.__tracer)

        for device in self.__devices:
            device.set_tracer(self.__tracer)

        for connection in self.__connections:
            connection.set_tracer(self.__tracer)

    @property
    def attacker(self):
        return self.__attacker

    @property
    def defender(self):
        return self.__defender

    @property
    def devices(self):
        return self.__devices

    @property
    def connections(self):
        return self.__connections

    @property
    def tracer(self):
        return self.__tracer

    def perform_attack(self, attack, target):
        return self.__attacker.perform_attack(attack, target)

    def inspect(self, target):
        return self.__defender.inspect(target)

    def block(self, target):
        self.__defender.block(target)

    def unblock(self, target):
        self.__defender.unblock(target)

    def isolate(self, target):
        self.__defender.isolate(target)

    def restore(self, target):
        self.__defender.restore(target)

    def secure_connection(self, connection):
        self.__defender.secure_connection(connection)

    def reset(self):
        for device in self.__devices:
            device.restore()
            device.unblock()

        for connection in self.__connections:
            connection.secure()
            connection.unblock()

        self.__tracer.clear()

    def __str__(self):
        return (
            f"Attacker: {self.__attacker.name} \t "
            f"Defender: {self.__defender.name} \t "
            f"Devices: {len(self.__devices)} \t "
            f"Connections: {len(self.__connections)}"
        )