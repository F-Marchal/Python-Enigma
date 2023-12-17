

__author__ = "Marchal Florent"
__copyright__ = "Copyright 2023, Marchal Florent"
__credits__ = ["Marchal Florent", ]
__license__ = "CC BY-NC-SA"
__version__ = "0.1.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "Prototype"

class EnigmaMachineError(Exception):
    pass

class MissingValueError(EnigmaMachineError):
    def __init__(self, missing, message):
        self.missing = missing
        super().__init__(message)

class RepeatedValueError(EnigmaMachineError):
    def __init__(self, repetition, message):
        self.repetition = repetition
        super().__init__(message)

class AsymmetricWire(EnigmaMachineError):


    def __init__(self, unknown, missing, message):
        self.unknown = unknown
        self.missing = missing
        super().__init__(message)


class NonLinearWire(EnigmaMachineError):
    def __init__(self, unknown, missing, message):
        self.unknown = unknown
        self.missing = missing
        super().__init__(message)

class NoRotorError(EnigmaMachineError):
    pass

class NoReflectorError(EnigmaMachineError):
    pass