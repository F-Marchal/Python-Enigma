"""This file is a python materialisation of the amazing work of Paul Reuvers and Frode Weierud:
    https://www.cryptomuseum.com/crypto/enigma/tree.htm

This file contain a number of class that contain rotors, reflectors and entry wells related to
historical iterations of the Enigma machine. (Of course, only, known model are present here.)

For each of these class, except <EnigmaContainer>, the docstring contain a link to the page of the cryptomuseum related
to the wiring of this Enigma machine.

Since (almost information) present here comes from the work of Paul Reuvers and Frode Weierud, I (Marchal Florent) do
give them all credits related to historical and technical information related to Enigma present
inside this file.
"""
__author__ = "Marchal Florent"
__credits__ = ["Paul Reuvers", "Frode Weierud"]
__version__ = "1.0.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "Production"

import Rotor
import Reflector
import ETW
import Enigma


class EnigmaContainer:
    """A class that is able to create a number of Rotors and EnigmaMachines related together.
    This class is used as a toolbox in order to define Groups of EnigmaMachines / Rotors / Reflectors / ETW that
    are supposed to be used together."""
    _alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @classmethod
    def getAlphabet(cls):
        """Return alphabet used by this set of rotors / machines."""
        return cls._alphabet

    @classmethod
    def toWire(cls, *values, reverse: bool = False) -> dict[int:int]:
        """Convert the order of a number of values intoo a wire for Rotors using <getAlphabet>"""

        if reverse:
            return Rotor.rapid_wire(*cls._alphabet, alphabet=values)
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


class EnigmaA133(EnigmaContainer):
    """Contain the rotors used in the A-133 machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#7."""
    _alphabet = "ABCDEFGHIJKLMNOPQRSTUVXYZÅÄÖ"

    @classmethod
    def getEnigmaB(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma B model A-133 with 3 of its rotors and its reflector.
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
        return ETW.ETW(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVXYZÅÄÖ"),
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


class EnigmaD(EnigmaContainer):
    """Contain the rotors used in the Enigma D machine.
    See https://www.cryptomuseum.com/crypto/enigma/wiring.htm#9"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma M4."""
        return ETW.ETW(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                       description="Enigma M4 - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"EKMFLGDQVZNTOWYHXUSPAIBRCJ"), turnovers=cls.toTurnover('Q'),
                           description="Enigma M4 - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"AJDKSIRUXBLHWTMCQGZNPYFVOE"), turnovers=cls.toTurnover('E'),
                           description="Enigma M4 - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"BDFHJLCPRTXVZNYEIWGAKMUSQO"), turnovers=cls.toTurnover('V'),
                           description="Enigma M4 - Rotor III")

    @classmethod
    def getRotorIV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor IV of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"ESOVPZJAYQUIRHXLNFTGKDCMWB"), turnovers=cls.toTurnover('J'),
                           description="Enigma M4 - Rotor IV")

    @classmethod
    def getRotorV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor V of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"VZBRGITYUPSDNHLXAWMJQOFECK"), turnovers=cls.toTurnover('Z'),
                           description="Enigma M4 - Rotor V")

    @classmethod
    def getRotorVI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VI of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"JPGVOUMFYQBENHZRDKASXLICTW"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M4 - Rotor VI")

    @classmethod
    def getRotorVII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VII of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"NZJHGRCXMYSWBOUFAIVLPEKQDT"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M4 - Rotor VII")

    @classmethod
    def getRotorVIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VIII of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"FKQHTLXOCBJSPDZRAMEWNIUYGV"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M4 - Rotor VIII")

    @classmethod
    def getReflectorBeta(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector Beta of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"LEYJVCNIXWPBQMDRTAKZGFUHOS"),
                                   description="Enigma M4 - Reflector Beta")

    @classmethod
    def getReflectorGamma(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector Gamma of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"FSOKANUERHMBTIYCWLQPZXVGJD"),
                                   description="Enigma M4 - Reflector Gamma")

    @classmethod
    def getReflectorUKWB(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKWB of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"ENKQAUYWJICOPBLMDXZVFTHRGS"),
                                   description="Enigma M4 - Reflector UKWB")

    @classmethod
    def getReflectorUKWC(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKWC of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"RDOBJNTKVEHMLFCWZAXGYIPSUQ"),
                                   description="Enigma M4 - Reflector UKWC")

    @classmethod
    def getEnigmaM4(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma M4 with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma M4 - 2 February 1942 - German Navy")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKWC())
        return enig


class EnigmaI(EnigmaContainer):
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
        return ETW.ETW(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
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


class EnigmaNorway(EnigmaContainer):
    """Contain the rotors used in the Norway Enigma machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#11"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma Norway."""
        return ETW.ETW(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                       description="Enigma Norway - ETW")
    
    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma Norway."""
        return Rotor.Rotor(wire=cls.toWire(*"WTOKASUYVRBXJHQCPZEFMDINLG"), turnovers=cls.toTurnover('Q'),
                           description="Enigma Norway - Rotor I")
    
    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma Norway."""
        return Rotor.Rotor(wire=cls.toWire(*"GJLPUBSWEMCTQVHXAOFZDRKYNI"), turnovers=cls.toTurnover('E'),
                           description="Enigma Norway - Rotor II")
    
    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma Norway."""
        return Rotor.Rotor(wire=cls.toWire(*"JWFMHNBPUSDYTIXVZGRQLAOEKC"), turnovers=cls.toTurnover('V'),
                           description="Enigma Norway - Rotor III")
    
    @classmethod
    def getRotorIV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor IV of an Enigma Norway."""
        return Rotor.Rotor(wire=cls.toWire(*"FGZJMVXEPBWSHQTLIUDYKCNRAO"), turnovers=cls.toTurnover('J'),
                           description="Enigma Norway - Rotor IV")
    
    @classmethod
    def getRotorV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor V of an Enigma Norway."""
        return Rotor.Rotor(wire=cls.toWire(*"HEJXQOTZBVFDASCILWPGYNMURK"), turnovers=cls.toTurnover('Z'),
                           description="Enigma Norway - Rotor V")
    
    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma Norway."""
        return Reflector.Reflector(wire=cls.toWire(*"MOWJYPUXNDSRAIBFVLKZGQCHET"),
                                   description="Enigma Norway - Reflector UKW")
    
    @classmethod
    def getEnigmaNorway(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma Norway with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma Norway - 1945 - Overvaakingspolitiet")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())
    
        enig.set_reflector(cls.getReflectorUKW())
        return enig


class A17401S(EnigmaContainer):
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma A-17401 S."""
        return ETW.ETW(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                       description="Enigma A-17401 S - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma A-17401 S."""
        return Rotor.Rotor(wire=cls.toWire(*"VEOSIRZUJDQCKGWYPNXAFLTHMB"), turnovers=cls.toTurnover('Q'),
                           description="Enigma A-17401 S - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma A-17401 S."""
        return Rotor.Rotor(wire=cls.toWire(*"UEMOATQLSHPKCYFWJZBGVXIDNR"), turnovers=cls.toTurnover('E'),
                           description="Enigma A-17401 S - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma A-17401 S."""
        return Rotor.Rotor(wire=cls.toWire(*"TZHXMBSIPNURJFDKEQVCWGLAOY"), turnovers=cls.toTurnover('V'),
                           description="Enigma A-17401 S - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma A-17401 S."""
        return Reflector.Reflector(wire=cls.toWire(*"CIAGSNDRBYTPZFULVHEKOQXWJM"),
                                   description="Enigma A-17401 S - Reflector UKW")

    @classmethod
    def getEnigmaA17401S(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma A-17401 S with its 3 rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma A-17401 S - special machine")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class EnigmaM3(EnigmaContainer):
    """Contain the rotors used in the Enigma M3 machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#13"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma M3."""
        return ETW.ETW(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                       description="Enigma M3 - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"EKMFLGDQVZNTOWYHXUSPAIBRCJ"), turnovers=cls.toTurnover('Q'),
                           description="Enigma M3 - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"AJDKSIRUXBLHWTMCQGZNPYFVOE"), turnovers=cls.toTurnover('E'),
                           description="Enigma M3 - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"BDFHJLCPRTXVZNYEIWGAKMUSQO"), turnovers=cls.toTurnover('V'),
                           description="Enigma M3 - Rotor III")

    @classmethod
    def getRotorIV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor IV of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"ESOVPZJAYQUIRHXLNFTGKDCMWB"), turnovers=cls.toTurnover('J'),
                           description="Enigma M3 - Rotor IV")

    @classmethod
    def getRotorV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor V of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"VZBRGITYUPSDNHLXAWMJQOFECK"), turnovers=cls.toTurnover('Z'),
                           description="Enigma M3 - Rotor V")

    @classmethod
    def getRotorVI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VI of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"JPGVOUMFYQBENHZRDKASXLICTW"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M3 - Rotor VI")

    @classmethod
    def getRotorVII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VII of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"NZJHGRCXMYSWBOUFAIVLPEKQDT"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M3 - Rotor VII")

    @classmethod
    def getRotorVIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VIII of an Enigma M3."""
        return Rotor.Rotor(wire=cls.toWire(*"FKQHTLXOCBJSPDZRAMEWNIUYGV"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M3 - Rotor VIII")

    @classmethod
    def getReflectorUKWB(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKWB of an Enigma M3."""
        return Reflector.Reflector(wire=cls.toWire(*"YRUHQSLDPXNGOKMIEBFZCWVJAT"),
                                   description="Enigma M3 - Reflector UKWB")

    @classmethod
    def getReflectorUKWC(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKWC of an Enigma M3."""
        return Reflector.Reflector(wire=cls.toWire(*"FVPJIAOYEDRZXWGCTKUQSBNMHL"),
                                   description="Enigma M3 - Reflector UKWC")

    @classmethod
    def getEnigmaM3(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma M3 with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma M3 - German Navy")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKWC())
        return enig


class EnigmaM4(EnigmaContainer):
    """Contain the rotors used in the Enigma M4 machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#14"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma M4."""
        return ETW.ETW(wire=cls.toWire(*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                       description="Enigma M4 - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"EKMFLGDQVZNTOWYHXUSPAIBRCJ"), turnovers=cls.toTurnover('Q'),
                           description="Enigma M4 - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"AJDKSIRUXBLHWTMCQGZNPYFVOE"), turnovers=cls.toTurnover('E'),
                           description="Enigma M4 - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"BDFHJLCPRTXVZNYEIWGAKMUSQO"), turnovers=cls.toTurnover('V'),
                           description="Enigma M4 - Rotor III")

    @classmethod
    def getRotorIV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor IV of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"ESOVPZJAYQUIRHXLNFTGKDCMWB"), turnovers=cls.toTurnover('J'),
                           description="Enigma M4 - Rotor IV")

    @classmethod
    def getRotorV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor V of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"VZBRGITYUPSDNHLXAWMJQOFECK"), turnovers=cls.toTurnover('Z'),
                           description="Enigma M4 - Rotor V")

    @classmethod
    def getRotorVI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VI of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"JPGVOUMFYQBENHZRDKASXLICTW"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M4 - Rotor VI")

    @classmethod
    def getRotorVII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VII of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"NZJHGRCXMYSWBOUFAIVLPEKQDT"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M4 - Rotor VII")

    @classmethod
    def getRotorVIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VIII of an Enigma M4."""
        return Rotor.Rotor(wire=cls.toWire(*"FKQHTLXOCBJSPDZRAMEWNIUYGV"), turnovers=cls.toTurnover(*'ZM'),
                           description="Enigma M4 - Rotor VIII")

    @classmethod
    def getReflectorBeta(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector Beta of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"LEYJVCNIXWPBQMDRTAKZGFUHOS"),
                                   description="Enigma M4 - Reflector Beta")

    @classmethod
    def getReflectorGamma(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector Gamma of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"FSOKANUERHMBTIYCWLQPZXVGJD"),
                                   description="Enigma M4 - Reflector Gamma")

    @classmethod
    def getReflectorUKWB(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKWB of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"ENKQAUYWJICOPBLMDXZVFTHRGS"),
                                   description="Enigma M4 - Reflector UKWB")

    @classmethod
    def getReflectorUKWC(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKWC of an Enigma M4."""
        return Reflector.Reflector(wire=cls.toWire(*"RDOBJNTKVEHMLFCWZAXGYIPSUQ"),
                                   description="Enigma M4 - Reflector UKWC")

    @classmethod
    def getEnigmaM4(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma M4 with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma M4 - 2 February 1942 - German Navy")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKWC())
        return enig


class EnigmaG(EnigmaContainer):
    """Contain the rotors used in the Enigma G machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#15"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma G."""
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
                       description="Enigma G - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma G."""
        return Rotor.Rotor(wire=cls.toWire(*"LPGSZMHAEOQKVXRFYBUTNICJDW"),
                           turnovers=cls.toTurnover(*'SUVWZABCEFGIKLOPQ'),
                           description="Enigma G - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma G."""
        return Rotor.Rotor(wire=cls.toWire(*"SLVGBTFXJQOHEWIRZYAMKPCNDU"), turnovers=cls.toTurnover(*'STVYZACDFGHKMNQ'),
                           description="Enigma G - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma G."""
        return Rotor.Rotor(wire=cls.toWire(*"CJGDPSHKTURAWZXFMYNQOBVLIE"), turnovers=cls.toTurnover(*'UWXAEFHKMNR'),
                           description="Enigma G - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma G."""
        return Reflector.Reflector(wire=cls.toWire(*"IMETCGFRAYSQBZXWLHKDVUPOJN"), rotation="normal",
                                   description="Enigma G - Reflector UKW")

    @classmethod
    def getEnigmaG(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma G with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma G - 1931")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class EnigmaG312(EnigmaContainer):
    """Contain the rotors used in the Enigma G312 machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#16"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma G31."""
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML", reverse=True),
                       description="Enigma G31 - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma G31."""
        return Rotor.Rotor(wire=cls.toWire(*"DMTWSILRUYQNKFEJCAZBPGXOHV"),
                           turnovers=cls.toTurnover(*'SUVWZABCEFGIKLOPQ'),
                           description="Enigma G31 - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma G31."""
        return Rotor.Rotor(wire=cls.toWire(*"HQZGPJTMOBLNCIFDYAWVEUSRKX"), turnovers=cls.toTurnover(*'STVYZACDFGHKMNQ'),
                           description="Enigma G31 - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma G31."""
        return Rotor.Rotor(wire=cls.toWire(*"UQNTLSZFMREHDPXKIBVYGJCWOA"), turnovers=cls.toTurnover(*'UWXAEFHKMNR'),
                           description="Enigma G31 - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma G31."""
        return Reflector.Reflector(wire=cls.toWire(*"RULQMZJSYGOCETKWDAHNBXPVIF"), rotation="normal",
                                   description="Enigma G31 - Reflector UKW")

    @classmethod
    def getEnigmaG31(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma G31 with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma G31 - 1931 - German Abwehr")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class EnigmaG260(EnigmaContainer):
    """Contain the rotors used in the Enigma G260 machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#17"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma G260."""
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
                       description="Enigma G260 - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma G260."""
        return Rotor.Rotor(wire=cls.toWire(*"RCSPBLKQAUMHWYTIFZVGOJNEXD"),
                           turnovers=cls.toTurnover(*'SUVWZABCEFGIKLOPQ'),
                           description="Enigma G260 - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma G260."""
        return Rotor.Rotor(wire=cls.toWire(*"WCMIBVPJXAROSGNDLZKEYHUFQT"), turnovers=cls.toTurnover(*'STVYZACDFGHKMNQ'),
                           description="Enigma G260 - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma G260."""
        return Rotor.Rotor(wire=cls.toWire(*"FVDHZELSQMAXOKYIWPGCBUJTNR"), turnovers=cls.toTurnover(*'UWXAEFHKMNR'),
                           description="Enigma G260 - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma G260."""
        return Reflector.Reflector(wire=cls.toWire(*"IMETCGFRAYSQBZXWLHKDVUPOJN"),
                                   description="Enigma G260 - Reflector UKW")

    @classmethod
    def getEnigmaG260(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma G260 with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma G260 - 1931 - German Abwehr")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class EnigmaG111(EnigmaContainer):
    """Contain the rotors used in the Enigma G111 machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#17
    Note that the wiring of the rotor III and IV are currently unknown.
    """

    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma G111."""
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
                       description="Enigma G111 - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma G111."""
        return Rotor.Rotor(wire=cls.toWire(*"WLRHBQUNDKJCZSEXOTMAGYFPVI"),
                           turnovers=cls.toTurnover(*'SUVWZABCEFGIKLOPQ'),
                           description="Enigma G111 - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma G111."""
        return Rotor.Rotor(wire=cls.toWire(*"TFJQAZWMHLCUIXRDYGOEVBNSKP"), turnovers=cls.toTurnover(*'STVYZACDFGHKMNQ'),
                           description="Enigma G111 - Rotor II")

    @classmethod
    def getRotorV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor V of an Enigma G111."""
        return Rotor.Rotor(wire=cls.toWire(*"QTPIXWVDFRMUSLJOHCANEZKYBG"), turnovers=cls.toTurnover(*'SWZFHMQ'),
                           description="Enigma G111 - Rotor V")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma G111."""
        return Reflector.Reflector(wire=cls.toWire(*"IMETCGFRAYSQBZXWLHKDVUPOJN"),
                                   description="Enigma G111 - Reflector UKW")

    @classmethod
    def getEnigmaG111(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma G111 with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma G111 - 1931 - Hungarian Army")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorV())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class EnigmaK(EnigmaContainer):
    """Contain the rotors used in the Enigma K machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#19"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma K."""
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
                       description="Enigma K - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma K."""
        return Rotor.Rotor(wire=cls.toWire(*"LPGSZMHAEOQKVXRFYBUTNICJDW"), turnovers=cls.toTurnover('Y'),
                           description="Enigma K - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma K."""
        return Rotor.Rotor(wire=cls.toWire(*"SLVGBTFXJQOHEWIRZYAMKPCNDU"), turnovers=cls.toTurnover('E'),
                           description="Enigma K - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma K."""
        return Rotor.Rotor(wire=cls.toWire(*"CJGDPSHKTURAWZXFMYNQOBVLIE"), turnovers=cls.toTurnover('N'),
                           description="Enigma K - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma K."""
        return Reflector.Reflector(wire=cls.toWire(*"IMETCGFRAYSQBZXWLHKDVUPOJN"),
                                   description="Enigma K - Reflector UKW")

    @classmethod
    def getEnigmaK(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma K with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma K - 1927 - Commercial model")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class SwissK(EnigmaContainer):
    """Contain the rotors used in the Swiss Enigma K variant machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#20."""

    @classmethod
    def getEnigmaK(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent a Swiss Enigma K variant with 3 of its rotors and
        its reflector.
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
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
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


class EnigmaKD(EnigmaContainer):
    """Contain the rotors used in the Enigma KD variant machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#22"""

    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma KD."""
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
                       description="Enigma KD - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma KD."""
        return Rotor.Rotor(wire=cls.toWire(*"VEZIOJCXKYDUNTWAPLQGBHSFMR"), turnovers=cls.toTurnover(*'SUYAEHLNQ'),
                           description="Enigma KD - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma KD."""
        return Rotor.Rotor(wire=cls.toWire(*"HGRBSJZETDLVPMQYCXAOKINFUW"), turnovers=cls.toTurnover(*'SUYAEHLNQ'),
                           description="Enigma KD - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma KD."""
        return Rotor.Rotor(wire=cls.toWire(*"NWLHXGRBYOJSAZDVTPKFQMEUIC"), turnovers=cls.toTurnover(*'SUYAEHLNQ'),
                           description="Enigma KD - Rotor III")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma KD.
        Note that in reality this UKW was rewindable. The permutations considered here was
        probably changed over time."""
        return Reflector.Reflector(wire=cls.toWire(*"KOTVPNLMJIAGHFBEWYXCZDQSRU"),
                                   description="Enigma KD - Reflector UKW")

    @classmethod
    def getEnigmaKD(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma KD with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma KD - 3 December 1944")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class EnigmaRailway(EnigmaContainer):
    """Contain the rotors used in the Railway Enigma machine.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#23"""
    @classmethod
    def getRocketI(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent a Railway Enigma with 3 of its rotors and its reflector.
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
        return ETW.ETW(wire=cls.toWire(*"QWERTZUIOASDFGHJKPYXCVBNML"),
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


class EnigmaT(EnigmaContainer):
    """Contain the rotors used in the Enigma T.
    All historical details came from "https://www.cryptomuseum.com/crypto/enigma/wiring.htm#25"""
    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma T."""
        return ETW.ETW(wire=cls.toWire(*"KZROUQHYAIGBLWVSTDXFPNMCJE"),
                       description="Enigma T - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"KPTYUELOCVGRFQDANJMBSWHZXI"), turnovers=cls.toTurnover(*'WZEKQ'),
                           description="Enigma T - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"UPHZLWEQMTDJXCAKSOIGVBYFNR"), turnovers=cls.toTurnover(*'WZFLR'),
                           description="Enigma T - Rotor II")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"QUDLYRFEKONVZAXWHMGPJBSICT"), turnovers=cls.toTurnover(*'WZEKQ'),
                           description="Enigma T - Rotor III")

    @classmethod
    def getRotorIV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor IV of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"CIWTBKXNRESPFLYDAGVHQUOJZM"), turnovers=cls.toTurnover(*'WZFLR'),
                           description="Enigma T - Rotor IV")

    @classmethod
    def getRotorV(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor V of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"UAXGISNJBVERDYLFZWTPCKOHMQ"), turnovers=cls.toTurnover(*'YCFKR'),
                           description="Enigma T - Rotor V")

    @classmethod
    def getRotorVI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VI of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"XFUZGALVHCNYSEWQTDMRBKPIOJ"), turnovers=cls.toTurnover(*'XEIMQ'),
                           description="Enigma T - Rotor VI")

    @classmethod
    def getRotorVII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VII of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"BJVFTXPLNAYOZIKWGDQERUCHSM"), turnovers=cls.toTurnover(*'YCFKR'),
                           description="Enigma T - Rotor VII")

    @classmethod
    def getRotorVIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor VIII of an Enigma T."""
        return Rotor.Rotor(wire=cls.toWire(*"YMTPNZHWKODAJXELUQVGCBISFR"), turnovers=cls.toTurnover(*'XEIMQ'),
                           description="Enigma T - Rotor VIII")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma T."""
        return Reflector.Reflector(wire=cls.toWire(*"GEKPBTAUMOCNILJDXZYFHWVQSR"),
                                   description="Enigma T - Reflector UKW")

    @classmethod
    def getEnigmaT(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma T with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Enigma T - 1930 - Japanese Navy / German Navy")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig


class EnigmaZ(EnigmaContainer):
    """Contain the rotors used in the Enigma Z.
    All historical details came from https://www.cryptomuseum.com/crypto/enigma/wiring.htm#26"""

    @classmethod
    def getETW(cls) -> ETW.ETW:
        """Return a ETW object that represent the entry wheel of an Enigma Z."""
        return ETW.ETW(wire=cls.toWire(*"1234567890"),
                       description="Enigma Z - ETW")

    @classmethod
    def getRotorI(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor I of an Enigma Z."""
        return Rotor.Rotor(wire=cls.toWire(*"6418270359"), turnovers=cls.toTurnover('9'),
                           description="Railway Enigma - Rotor I")

    @classmethod
    def getRotorII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor II of an Enigma Z."""
        return Rotor.Rotor(wire=cls.toWire(*"5841097632"), turnovers=cls.toTurnover('9'),
                           description="Railway Enigma - Rotor I")

    @classmethod
    def getRotorIII(cls) -> Rotor.Rotor:
        """Return a Rotor object that represent the Rotor III of an Enigma Z."""
        return Rotor.Rotor(wire=cls.toWire(*"3581620794"), turnovers=cls.toTurnover('9'),
                           description="Railway Enigma - Rotor I")

    @classmethod
    def getReflectorUKW(cls) -> Reflector.Reflector:
        """Return a Reflector object that represent the reflector UKW of an Enigma Z."""
        return Reflector.Reflector(wire=cls.toWire(*"5079183642"), turnovers=cls.toTurnover('9'), rotation="normal",
                                   description="Enigma Z - Reflector UKW")

    @classmethod
    def getEnigmaZ(cls) -> Enigma.EnigmaMachine:
        """Return an EnigmaMachine object that represent an Enigma Z with 3 of its rotors and one reflector.
        """
        enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                    description="Railway Enigma - Switzerland")
        enig.load_rotor(cls.getRotorI())
        enig.load_rotor(cls.getRotorII())
        enig.load_rotor(cls.getRotorIII())

        enig.set_reflector(cls.getReflectorUKW())
        return enig

def load_tab():
    name = "Enigma A-17401 S"
    detailes = "special machine"
    if len(detailes) != 0 and detailes[0:3] != " - ":
        detailes = " - " + detailes
    TAB = """Rotor 	ABCDEFGHIJKLMNOPQRSTUVWXYZ 	Notch 	Turnover 	#
    ETW 	ABCDEFGHIJKLMNOPQRSTUVWXYZ 	  	  	 
    I 	VEOSIRZUJDQCKGWYPNXAFLTHMB 	Y 	Q 	1
    II 	UEMOATQLSHPKCYFWJZBGVXIDNR 	M 	E 	1
    III 	TZHXMBSIPNURJFDKEQVCWGLAOY 	D 	V 	1
    UKW 	CIAGSNDRBYTPZFULVHEKOQXWJM 	  	  	 
    """
    f_3 = []
    a = "an" if name[0].lower() in 'aoiuey' else "a"
    ukw = None
    for lines in TAB.split("\n"):
        lines = lines.split("\t")
        first = lines[0].strip()

        if len(lines) < 2:
            continue
        if first == 'Rotor':
            continue
        first = first.replace("-", "")
        seq = lines[1].strip()
        turnover = f"'{lines[3].strip()}'" if len(lines[3].strip()) == 1 else f"*'{lines[3].strip()}'"
        if first == "ETW":
            print(f'''    @classmethod\n    def getETW(cls) -> ETW.ETW:
            """Return a ETW object that represent the entry wheel of {a} {name}."""
            return ETW.ETW(wire=cls.toWire(*"{seq}"),
                           description="{name} - ETW")''')
            print()

        elif "UKW" in first or "Gamma" in first or "Beta" in first:

            print(f'''    @classmethod\n    def getReflector{first}(cls) -> Reflector.Reflector:
            """Return a Reflector object that represent the reflector {first} of {a} {name}."""
            return Reflector.Reflector(wire=cls.toWire(*"{seq}"),
                                       description="{name} - Reflector {first}")''')
            print()
            ukw = f'''getReflector{first}()'''

        else:
            print(f'''    @classmethod\n    def getRotor{first}(cls) -> Rotor.Rotor:
                """Return a Rotor object that represent the Rotor {first} of {a} {name}."""
                return Rotor.Rotor(wire=cls.toWire(*"{seq}"), turnovers=cls.toTurnover({turnover}),
                                   description="{name} - Rotor {first}")''')
            print()
            if len(f_3) == 3:
                continue
            f_3.append(f"""getRotor{first}()""")

    rotors = ""
    for items in f_3:
        rotors += f"enig.load_rotor(cls.{items})\n        "
    print(f'''    @classmethod
        def get{name.replace(" ", "")}(cls) -> Enigma.EnigmaMachine:
            """Return an EnigmaMachine object that represent {a} {name} with its {len(f_3)} rotors and one reflector.
            """
            enig = Enigma.EnigmaMachine(len(cls.getAlphabet()), translator=cls.getAlphabet(), etw=cls.getETW(),
                                        description="{name}{detailes}")
            {rotors}
            enig.set_reflector(cls.{ukw})
            return enig''')