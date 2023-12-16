"""This file is a python materialisation of the amazing work of Paul Reuvers and Frode Weierud.
See https://www.cryptomuseum.com/crypto/enigma/tree.htm



"""
__author__ = "Marchal Florent"
__copyright__ = "Copyright 2023, Paul Reuvers and Frode Weierud"
__credits__ = ["Paul Reuvers", "Frode Weierud"]
__license__ = "-"
__version__ = "1.0.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "?"

import Rotor
import Reflector
import ETW
import Enigma


class HistoricalContainer:
    """A class that is able to create a number of Rotors and EnigmaMachines related together.
    This class is used as a toolbox in order to define EnigmaMachines used by the past with their rotors."""
    _alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @classmethod
    def getAlphabet(cls):
        """Return alphabet used by this set of rotors / machines."""
        return cls._alphabet

    @classmethod
    def toWire(cls, *values) -> dict[int:int]:
        """Convert the order of a number of values intoo a wire for Rotors using <getAlphabet>"""
        return Rotor.rapid_wire(*values, alphabet=cls._alphabet)

    @classmethod
    def toPosition(cls, value) -> int:
        """Convert value intoo an index that correspond to Rotor's position using <getAlphabet>"""
        return cls._alphabet.index(value)

    @classmethod
    def toTurnover(cls, *values) -> set[int]:
        """Convert a number of values intoo a set of turnover using <getAlphabet>"""
        r_values = set()
        for val in values:
            r_values.add(cls._alphabet.index(val))
        return r_values


class A133(HistoricalContainer):
    """Contain the rotors used in the A-133 machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#7."""
    _alphabet = "ABCDEFGHIJKLMNOPQRSTUVXYZÅÄÖ"

    @classmethod
    def getEnigmaB(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma B model A-133 with its 3 rotors and its reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma B model A-133 - 6 April 1925 - Swedish SGS")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())
        enig.set_reflector(cls.getReflectorUKW())
        return enig

    @classmethod
    def getETW(cls):
        """Return a ETW object that represent entry wheel of an Enigma B model A-133."""
        return Rotor.Rotor(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVXYZÅÄÖ"),
                           description="Enigma B model A-133 - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor I of an Enigma B model A-133."""
        return Rotor.Rotor(wire=cls.toWire(*"PSBGÖXQJDHOÄUCFRTEZVÅINLYMKA"), turnovers=cls.toTurnover("Ä"),
                           description="Enigma B model A-133 - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor II of an Enigma B model A-133."""
        return Rotor.Rotor(wire=cls.toWire(*"CHNSYÖADMOTRZXBÄIGÅEKQUPFLVJ"), turnovers=cls.toTurnover("Ä"),
                           description="Enigma B model A-133 - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor III of an Enigma B model A-133."""
        return Rotor.Rotor(wire=cls.toWire(*"ÅVQIAÄXRJBÖZSPCFYUNTHDOMEKGL"), turnovers=cls.toTurnover("Ä"),
                           description="Enigma B model A-133 - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma B model A-133."""
        return Reflector.Reflector(wire=cls.toWire(*"LDGBÄNCPSKJAVFZHXUIÅRMQÖOTEY"),
                                   description="Enigma B model A-133 - Reflector UKW")


class EnigmaD(HistoricalContainer):
    """Contain the rotors used in the Enigma D machine.
    See https://www.cryptomuseum.com/crypto/enigma/wiring.htm#9"""


class EnigmaI(HistoricalContainer):
    """Contain the rotors used in the Enigma I machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#10"""

    @classmethod
    def getEnigmaI(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma I with 3 of his rotors and one UKWA reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma I - 6 April 1925 - Swedish SGS")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())
        enig.set_reflector(cls.getReflectorUKWA())
        return enig

    @classmethod
    def getETW(cls):
        """Return a ETW object that represent entry wheel of an Enigma I."""
        return Rotor.Rotor(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                           description="Enigma I - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor I of an Enigma I."""
        return Rotor.Rotor(wire=cls.toWire(*"EKMFLGDQVZNTOWYHXUSPAIBRCJ"), turnovers=cls.toTurnover("Q"),
                           description="Enigma I - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor II of an Enigma I."""
        return Rotor.Rotor(wire=cls.toWire(*"AJDKSIRUXBLHWTMCQGZNPYFVOE"), turnovers=cls.toTurnover("E"),
                           description="Enigma I - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor III of an Enigma I."""
        return Rotor.Rotor(wire=cls.toWire(*"BDFHJLCPRTXVZNYEIWGAKMUSQO"), turnovers=cls.toTurnover("V"),
                           description="Enigma I - Rotor III")

    @classmethod
    def getRotorIV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor IV of an Enigma I."""
        return Rotor.Rotor(wire=cls.toWire(*"ESOVPZJAYQUIRHXLNFTGKDCMWB"), turnovers=cls.toTurnover("J"),
                           description="Enigma I - Rotor IV")
                           
    @classmethod
    def getRotorV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor V of an Enigma I."""
        return Rotor.Rotor(wire=cls.toWire(*"VZBRGITYUPSDNHLXAWMJQOFECK"), turnovers=cls.toTurnover("V"),
                           description="Enigma I - Rotor V")
                           
    @classmethod
    def getReflectorUKWA(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector III of an Enigma I."""
        return Reflector.Reflector(wire=cls.toWire(*"EJMZALYXVBWFCRQUONTSPIKHGD"),
                                   description="Enigma I - Reflector UKWA")

    @classmethod
    def getReflectorUKWB(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector III of an Enigma I."""
        return Reflector.Reflector(wire=cls.toWire(*"YRUHQSLDPXNGOKMIEBFZCWVJAT"),
                                   description="Enigma I - Reflector UKWB")

    @classmethod
    def getReflectorUKWC(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector III of an Enigma I."""
        return Reflector.Reflector(wire=cls.toWire(*"FVPJIAOYEDRZXWGCTKUQSBNMHL"),
                                   description="Enigma I - Reflector UKWC")


class EnigmaM3(HistoricalContainer):
    """https://www.cryptomuseum.com/crypto/enigma/wiring.htm#13"""


class EnigmaM4(HistoricalContainer):
    """https://www.cryptomuseum.com/crypto/enigma/wiring.htm#14"""


class EnigmaG(HistoricalContainer):
    """https://www.cryptomuseum.com/crypto/enigma/wiring.htm#15"""


class EnigmaK(HistoricalContainer):
    """https://www.cryptomuseum.com/crypto/enigma/wiring.htm#19"""


class SwissK(HistoricalContainer):
    """Contain the rotors used in the Swiss Enigma K variant machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#20."""

    @classmethod
    def getEnigmaK(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent a Swiss Enigma K variant with its 3 rotors and its reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Swiss Enigma K variant - 1939 - Switzerland")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())
        enig.set_reflector(cls.getReflectorUKW())
        return enig

    @classmethod
    def getETW(cls):
        """Return a ETW object that represent the entry wheel of a Swiss Enigma K variant."""
        return Rotor.Rotor(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
                           description="Swiss Enigma K variant - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor I of a Swiss Enigma K variant."""
        return Rotor.Rotor(wire=cls.toWire(*"PEZUOHXSCVFMTBGLRINQJWAYDK"), turnovers=cls.toTurnover("Y"),
                           description="Swiss Enigma K variant - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor II of a Swiss Enigma K variant."""
        return Rotor.Rotor(wire=cls.toWire(*"ZOUESYDKFWPCIQXHMVBLGNJRAT"), turnovers=cls.toTurnover("E"),
                           description="Swiss Enigma K variant - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor III of a Swiss Enigma K variant."""
        return Rotor.Rotor(wire=cls.toWire(*"EHRVXGAOBQUSIMZFLYNWKTPDJC"), turnovers=cls.toTurnover("N"),
                           description="Swiss Enigma K variant - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of a Swiss Enigma K variant."""
        return Reflector.Reflector(wire=cls.toWire(*"IMETCGFRAYSQBZXWLHKDVUPOJN"),
                                   description="Swiss Enigma K variant - Reflector UKW")


class EnigmaKD(HistoricalContainer):
    """https://www.cryptomuseum.com/crypto/enigma/wiring.htm#22"""


class RailwayEnigma(HistoricalContainer):
    """Contain the rotors used in the Railway Enigma machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#23"""
    @classmethod
    def getRailwayEnigma(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent a Railway Enigma with its 3 rotors and its reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Railway Enigma - Switzerland")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())
        enig.set_reflector(cls.getReflectorUKW())
        return enig

    @classmethod
    def getETW(cls):
        """Return a ETW object that represent the entry wheel of a Railway Enigma."""
        return Rotor.Rotor(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
                           description="Railway Enigma - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor I of a Railway Enigma."""
        return Rotor.Rotor(wire=cls.toWire(*"JGDQOXUSCAMIFRVTPNEWKBLZYH"), turnovers=cls.toTurnover("N"),
                           description="Railway Enigma - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor II of a Railway Enigma."""
        return Rotor.Rotor(wire=cls.toWire(*"NTZPSFBOKMWRCJDIVLAEYUXHGQ"), turnovers=cls.toTurnover("E"),
                           description="Railway Enigma - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the rotor III of a Railway Enigma."""
        return Rotor.Rotor(wire=cls.toWire(*"JVIUBHTCDYAKEQZPOSGXNRMWFL"), turnovers=cls.toTurnover("Y"),
                           description="Railway Enigma - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of a Railway Enigma."""
        return Reflector.Reflector(wire=cls.toWire(*"QYHOGNECVPUZTFDJAXWMKISRBL"),
                                   description="Railway Enigma - Reflector UKW")


class EnigmaT(HistoricalContainer):
    """https://www.cryptomuseum.com/crypto/enigma/wiring.htm#25"""


class EnigmaZ(HistoricalContainer):
    """https://www.cryptomuseum.com/crypto/enigma/wiring.htm#26"""



swissk = SwissK.getEnigmaK()
print(swissk.encode("A"))
print(swissk.encode("A"))
print(swissk.encode("A"))
