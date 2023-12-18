"""A file that contain custom errors related to Enigma.
Is a part of the 'Enigma' package."""
__author__ = "Marchal Florent"
__copyright__ = "Copyright 2023, Marchal Florent"
__credits__ = ["Marchal Florent", ]
__license__ = "CC BY-NC-SA"
__version__ = "1.0.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "Production"


class EnigmaMachineError(Exception):
    """An Error that is the parent of all other error related to enigma machine."""


class MissingValueError(EnigmaMachineError):
    """An Error that is raised when a value is missing inside a wire or a translator"""
    def __init__(self, missing, message):
        self.missing = missing
        super().__init__(message)


class RepeatedValueError(EnigmaMachineError):
    """An Error that is raised when values are repeated inside a wire or a translator"""
    def __init__(self, repetition, message):
        self.repetition = repetition
        super().__init__(message)


class AsymmetricWire(EnigmaMachineError):
    """An Error that is raised when values is the front part of a wire are not the same in the back part of a wire."""
    def __init__(self, unknown, missing, message):
        self.unknown = unknown
        self.missing = missing
        super().__init__(message)


class NonLinearWire(EnigmaMachineError):
    """An Error that is raised when there is gap inside a wire."""
    def __init__(self, unknown, missing, message):
        self.unknown = unknown
        self.missing = missing
        super().__init__(message)


class NoRotorError(EnigmaMachineError):
    """An Error that is raised when there is no rotor inside an EnigmaMachine."""


class NoReflectorError(EnigmaMachineError):
    """An Error that is raised when there is no reflector inside an EnigmaMachine."""
