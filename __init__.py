# encoding=UTF-8
"""This package provide objects that can be used to emulate an Enigma machine.

=== === === === Objects and modules === === === ===
Objects that you can find inside this package are:

Rotor : Is made to emulate a rotors used by Enigma:
    ETW : A Special kind of Rotor that represent the entry wheels (the element that link the keyboard and the rotor)
    Reflector : A Special kind of rotor that can be used as reflector (UKW). The wiring of this king of rotor has to
                be "symmetrical".

EnigmaMachine : The main object of this package. This object require the creation of Rotors object to
                work as intended.

Specials errors raised by this package can be found in the "Errors" module.

Known model of Rotor / Reflector / EnigmaMachine can be found inside  the 'Historical' module.

Debugging of the machine was done using the following websites :
    https://www.cryptool.org/en/cto/enigma-step-by-step
    https://cryptii.com/pipes/enigma-machine

Review log :
18/12/2023 → Status set to "Production"
"""
__author__ = "Marchal Florent"
__copyright__ = "Copyright 2023, Marchal Florent"
__credits__ = ["Marchal Florent", ]
__license__ = "CC BY-NC-SA"
__version__ = "1.0.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "Production"

import Historical
import Errors
from ETW import ETW
from Reflector import Reflector
from Rotor import Rotor, rapid_wire
from Enigma import EnigmaMachine


