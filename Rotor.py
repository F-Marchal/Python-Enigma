# encoding=UTF-8
"""Provide an object that represent a rotors for an Enigma machine (the german cypher machine).
This class can be used as a reflector.
Is a part of the 'Enigma' package.

You can find two example at the bottom of this file.

Review log :
19/11/2023 → File status set to "Production"
23/11/2023 → new method : can_rotate
28/11/2023 → <Rotor.rotation> can be set using None.
"""

__author__ = "Marchal Florent"
__copyright__ = "Copyright 2023, Marchal Florent"
__credits__ = ["Marchal Florent", ]
__license__ = "CC BY-NC-SA"
__version__ = "1.0.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "Production"

from Errors import AsymmetricWire, NonLinearWire


class Rotor:
    """Represent a Rotor used by an Enigma machine. It also can fulfill the role of reflector.
    Rotors can only scramble integer greater or equal to 0 and lower than the number of values inside Rotor's wire for
    speed purposes. Use Rotors inside a EnigmaMachine if you want to use them to translate anny other values (such
    as characters).

    Attributes :
    wire (dict)
    reversed_wire (dict)
    offset (int)
    position (int)
    notches (set) and overflows (int)
    rotation (str)
    length (int)
    modifier (int)
    """

    # special methods
    def __init__(self, wire: list[int] or tuple[int] or dict[int],
                 offset: int = 0,
                 position: int = 0,
                 notches: int or tuple[int] or list[int] or set[int] = None,
                 overflows: int or tuple[int] or list[int] or set[int] = None,
                 rotation: str = None,
                 description=None,
                 ):
        """
        :param list, tuple, dict wire :
            The <wire> is the part that scramble values passed inside the Rotor. Values inside the <wire> has to be
            integer (for speed purpose).
                - Can be set using a list or a tuple of integer. In this case the Rotor assume that the <wire> is a
                    dictionary using the following formula : {i: value for i, value in enumerate(<wire>)}
                - Can be set using a dictionary of integer. The scramble is made using the key / value association.
            <wire> should follow a number of rules detailed inside <self._wire_inspection>.

        :param int position:
            The current position of this Rotor. On a normal Enigma this corresponds to the value displayed in top of
            the machine (e.g: 'A', 'B', 'C', ...) and to machine's "key".
            Must be an integer between 0 and <wire>'s length (len(<wire>)).

        :param int offset:
            Shift the <wire>'s key / value combinations by n.
            Must be an integer between 0 and <wire>'s length (len(<wire>)).

        :param list, tuple, set notches:
            /!\\ Overwrite overflows
            When Rotor's position QUIT a notch the next rotor has his position changed.
            Must be a list or a tuple or a set of integer between 0 and <wire>'s length (len(<wire>)).

        :param list, tuple, set overflows:
            /!\\ Overwrite by notches /!\\
            When Rotor's position REACH an overflows the next rotor has his position changed.
            Must be a list or a tuple or a set of integer between 0 and <wire>'s length (len(<wire>)).

        :param str rotation:
            'normal' or 'reversed' or 'without' or None.
            Modify how this Rotor can turn.
                - 'normal' - This rotor turn in the normal way : Position increase at each <self.turn()>
                - 'reversed' - This rotor turn in the opposite way : Position decrease at each <self.turn()>
                - 'without' - This rotor do not turn but next rotor can turn if previous rotor turn.

        :param description: A description of this Rotor. Generally historical or usage information.
        """
        # Wire
        wire = self._wire_inspection(wire)
        self._wire = wire
        self._reverse_wire = {value: key for value, key in wire.items()}

        # Other
        self._length = len(wire)
        self.position = position
        self.offset = offset
        self.rotation = rotation
        self.description = description
        
        # Notches
        self._notches = set()
        if notches:
            self.notches = notches
        elif overflows:
            self.overflows = overflows
        else:
            self.notches = None

    def __copy__(self):
        """Return a new independent rotor based on this one"""
        type_ = self.__class__
        return type_(**self.get_full_configuration())

    # normal methods
    def set_notches(self, *values: int):
        """/!\\ Overwrite overflows /!\\
        Change the set of values used as notches.
        :param int values:
            Values now used as notches. They have to be integer greater or equal 0 and lower than <self._length>
        :raise ValueError: When values are not integer greater or equal 0 and lower than <self._length>
        """
        for item in values:
            if not self.is_in_range(item):
                raise ValueError(f"Integer greater or equal to 0 and lower than <self._length> expected. Got : {item}")

        self._notches.clear()
        self._notches |= set(values)

    def set_overflow(self, *values: int):
        """/!\\ Overwrite notches /!\\
        Change the set of values used as overflows. This is function call <self.set_notches>
        :param int values:
            Values now used as notches. They have to be integer greater or equal 0 and lower than <self._length>"""
        self.set_notches(*[value - 1 if isinstance(value, int) else value for value in values])

    def forward_reading(self, value: int):
        """Scramble a value with the <self.wire>. Correspond to how values are treat between the keyboard and the
        reflector.
        :param int value: An integer to scramble. Not that this function will use <value> modulo <self.length>.
        """
        modifier = self.modifier
        return (self._wire[(value + modifier) % self._length] - modifier) % self._length

    def backward_reading(self, value: int):
        """Scramble a value with the <self.wire>. Correspond to how values are treat between the reflector and the
        light panel.
        :param int value: An integer to scramble. Not that this function will use <value> modulo <self.length>.
        """
        modifier = self.modifier
        return (self._reverse_wire[(value + modifier) % self._length] - modifier) % self._length

    def turn(self) -> bool:
        """Turn the rotor of one step and return True if the next rotor should turn.
        /!\\ if <self.rotation> is "without" the position won't change.
        Use <self.rotation> to control the direction of rotation.
        If you want to turn the rotor until it reach a certain value without using the boolean returned by <self.turn>,
            you might want to simply set <self.position> to the value that you want.
        :return bool: Do this rotor QUIT a notch.
        """
        bool_ = self._position in self._notches
        if self._rotation == "normal":
            self.position += 1
        elif self._rotation == "reversed":
            self.position -= 1
        elif self._rotation == "without":
            return True

        return bool_

    def can_rotate(self) -> bool:
        """Say if this rotor can rotate. Note that even if this rotor can not turn, the <turn> method will not
        raise error."""
        return self._rotation != "without"

    def is_in_range(self, value: int) -> bool:
        """Do a value is an integer greater than 0 and lower than <self.length>"""
        return isinstance(value, int) and 0 <= value < self._length

    def configure(self, offset=None, position: int = None, rotation: str = None,
                  notches: int or tuple[int] or list[int] or set[int] = None,
                  overflows: int or tuple[int] or list[int] or set[int] = None,
                  description=None):
        """Modify the value of a number of attributes. Use it in conjunction with <self.get_configuration> to restore
        the configuration oof this Rotor.
        :param int position:
            The current position of this Rotor. On a normal Enigma this corresponds to the value displayed in top of
            the machine (e.g: 'A', 'B', 'C', ...) and to machine's "key".
            Must be an integer between 0 and <wire>'s length (len(<wire>)).

        :param int offset:
            Shift the <wire>'s key / value combinations by n.
            Must be an integer between 0 and <wire>'s length (len(<wire>)).

        :param list, tuple, set notches:
            /!\\ Overwrite overflows
            When Rotor's position QUIT a notch the next rotor has his position changed.
            Must be a list or a tuple or a set of integer between 0 and <wire>'s length (len(<wire>)).

        :param list, tuple, set overflows:
            /!\\ Overwrite by notches /!\\
            When Rotor's position REACH an overflows the next rotor has his position changed.
            Must be a list or a tuple or a set of integer between 0 and <wire>'s length (len(<wire>)).

        :param str rotation:
            'normal' or 'reversed' or 'without'.
            Modify how this Rotor can turn.
                - 'normal' - This rotor turn in the normal way : Position increase at each <self.turn()>
                - 'reversed' - This rotor turn in the opposite way : Position decrease at each <self.turn()>
                - 'without' - This rotor do not turn but next rotor can turn if previous rotor turn.

        :param description: A description of this Rotor. Generally historical or usage information.
        """
        if offset: self.offset = offset
        if position: self.position = position
        if notches: self.notches = notches
        elif overflows: self.overflows = overflows
        if rotation: self.rotation = rotation
        if description: self.description = description

    def get_configuration(self) -> dict:
        """Give the current configuration of this rotor. You can use this dictionary in order to save Rotor's
        Configuration"""
        return {
            "position": self.offset,
            "offset": self.position,
            "notches": self.notches,
            "rotation": self.rotation
        }

    def get_full_configuration(self):
        """Give the current configuration of this rotor. You can use this dictionary in order create a
        brand-new rotor."""
        dict_ = self.get_configuration()
        dict_.update({
            "wire": self.wire,
            "description": self.description,
        })
        return dict_

    def copy(self):
        """Return a new independent rotor based on this one"""
        return self.__copy__()

    # private methods
    @staticmethod
    def _wire_inspection(wire: list[int] or tuple[int] or dict[int]) -> dict[int:int]:
        """Internal Function. Return a wire that can be used by a Rotor.
        A wire is a dict that respect the following rules:
            A: All keys are integer between 0 and dictionary's length.
            B: All values are also keys
            C: All keys are also values
        :return dict: A functional dictionary"""
        if isinstance(wire, (list, tuple)):
            wire = {i: value for i, value in enumerate(wire)}

        elif not isinstance(wire, dict):
            # Assure that <wire> is a dict or a list or a tuple.
            raise TypeError(f"<wire> should be dict or list or tuple. Got : {type(wire)}")

            # minimal length
        length = len(wire)
        if length < 2:
            raise IndexError("At least two key are expected inside <wire>.")

        # All keys are integer between 0 and dictionary's length.
        if set(wire.keys()) != set(range(0, length)):
            set_ = set(range(0, length))
            unknown = set(wire.keys()).difference(set_)
            missing = set_.difference(wire.keys())
            raise NonLinearWire(unknown, missing, "<wire>'s keys should be a range from 0 to n in any order. Got : \n"
                                                  f"{len(unknown)} unknown value(s) : {unknown}\n"
                                                  f"{len(missing)} missing value(s) : {missing}")

        # Asymmetrical wire : All keys should be values and all values should be keys.
        if set(wire.keys()) != set(wire.values()):
            unknown = set(wire.values()).difference(wire.keys())
            missing = set(wire.keys()).difference(wire.values())
            raise AsymmetricWire(unknown, missing, "<wire>'s keys and values should be the sames. Got : \n"
                                                   f"{len(unknown)} unknown value(s) : {unknown}\n"
                                                   f"{len(missing)} missing value(s) : {missing}")
        return wire

    # Getter only attributes
    @property
    def wire(self) -> dict:
        """Give a copy of Rotor's wire.
        The <wire> is the part that scramble values passed inside the Rotor. Values inside the <wire> are
        integer (for speed purpose)."""
        return self._wire.copy()

    @property
    def reversed_wire(self) -> dict:
        """Give a copy of Rotor's wire but with keys and values unversed.
        The <wire> is the part that scramble values passed inside the Rotor. Values inside the <wire> are
        integer (for speed purpose)."""
        return self._reverse_wire.copy()

    @property
    def length(self) -> int:
        """How many values are inside this Rotor."""
        return self._length

    @property
    def modifier(self) -> int:
        """Summarize the effect of <self.offset> and <self.position> on wire reading.
        :return int: An integer greater than  -1 * <self.length> and lower than <self.length>"""
        return self._position - self._offset

    # Getter / setter attributes
    @property
    def offset(self) -> int:
        """Shift the <wire>'s key / value combinations by n.
        :return int: integer between 0 and <wire>'s length (len(<wire>))."""
        return self._offset

    @offset.setter
    def offset(self, n: int):
        """Shift the <wire>'s key / value combinations by <n>.
        must be an integer between 0 and <wire>'s length (len(<wire>))."""
        if not self.is_in_range(n):
            raise ValueError(f"Integer greater or equal to 0 and lower than <self._length> expected. Got : {n}")
        self._offset = n

    @property
    def position(self) -> int:
        """The current position of this Rotor. On a normal Enigma this corresponds to the value displayed in top of
        the machine (e.g: 'A', 'B', 'C', ...) and to machine's "key".
        :return int : An integer between 0 and <wire>'s length (len(<wire>)).
        """
        return self._position

    @position.setter
    def position(self, value: int):
        """The current position of this Rotor. On a normal Enigma this corresponds to the value displayed in top of
        the machine (e.g: 'A', 'B', 'C', ...) and to machine's "key".
        :param value: An integer between 0 and <wire>'s length (len(<wire>)).
        """
        if not isinstance(value, int):
            raise ValueError(f"Integer expected. Got : {value}")
        self._position = value % self._length

    @property
    def rotation(self) -> str:
        """How this rotor can turn
        :return str:  'normal' or 'reversed' or 'without'.
            - 'normal' - This rotor turn in the normal way : Position increase at each <self.turn()>
            - 'reversed' - This rotor turn in the opposite way : Position decrease at each <self.turn()>
            - 'without' - This rotor do not turn but next rotor can turn if previous rotor turn."""
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        """
        Modify how this Rotor can turn.
        'normal' or 'reversed' or 'without' or None.
            - 'normal' or None - This rotor turn in the normal way : Position increase at each <self.turn()>
            - 'reversed' - This rotor turn in the opposite way : Position decrease at each <self.turn()>
            - 'without' - This rotor do not turn but next rotor can turn if previous rotor turn.
        """
        if value is None:
            value = "normal"
        if not isinstance(value, str) or value.lower() not in ('normal', 'reversed', 'without'):
            raise ValueError(f"expect 'normal', 'reversed' or 'without'. got : {value}")

        self._rotation = value.lower()

    @property
    def notches(self) -> set[int]:
        """:return set: a set of notches currently used by this rotor.
        When Rotor's position QUIT a notch the next rotor has his
        position changed. Must be a list or a tuple or a set of integer between 0 and <wire>'s length (len(<wire>))."""
        return self._notches.copy()

    @notches.setter
    def notches(self, value: int or tuple[int] or list[int] or set[int]):
        """/!\\ Overwrite overflows /!\\
        Change the set of values used as notches. See <self.set_notches> for more information.
        :param int, tuple, list, set value:
            An integer or a number of integer greater or equal to 0 and lower than Rotor's length"""
        if value is None:
            value = set()
        self.set_notches(*value) if isinstance(value, (tuple, set, list)) else [value]

    @property
    def overflows(self):
        """:return set: a set of overflows currently used by this rotor.
        When Rotor's position REACH a notch the next rotor has his
        position changed. Must be a list or a tuple or a set of integer between 0 and <wire>'s length (len(<wire>))."""
        return {value + 1 for value in self._notches}

    @overflows.setter
    def overflows(self, value: int or tuple[int] or list[int] or set[int]):
        """/!\\ Overwrite notches /!\\
        Change the set of values used as overflows. See <self.set_notches> for more information.
        :param int, tuple, list, set value:
            An integer or a number of integer greater or equal to 0 and lower than Rotor's length"""
        if value is None:
            value = set()
        self.set_overflow(*value) if isinstance(value, (tuple, set, list)) else [value]
    
    @property
    def description(self):
        """A description of this Rotor. Generally contain historical or usage information."""
        return self._description
    
    @description.setter
    def description(self, value):
        """A description of this Rotor. Generally historical or usage information."""
        self._description = value

if __name__ == '__main__':
    #  --- --- Creation of IC rotor from commercial Enigma at the position "D" and with an offset of 5 --- ---
    #  ---  Wire creation ---
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    wire_ic = "DMTWSILRUYQNKFEJCAZBPGXOHV"

    # Translate letters in integer using their place inside the alphabet
    wire_ic = [alphabet.index(char) for char in wire_ic]

    # --- Init the rotor ---
    ic = Rotor(wire=wire_ic, notches={alphabet.index("Q")}, position=alphabet.index("D"), offset=5)

    #  --- --- Creation of UKWA reflector --- ---
    #  ---  Wire creation ---
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letter_swap = "AY BR CU DH EQ FS GL IP JX KN MO TZ VW"

    # Translate letters in integer using their place inside the alphabet
    letter_swap = letter_swap.split(" ")
    ukw_wire = {alphabet.index(a): alphabet.index(b) for a, b in letter_swap}
    ukw_wire.update({alphabet.index(b): alphabet.index(a) for a, b in letter_swap})

    # --- Init the reflector ---
    ukw_a = Rotor(wire=ukw_wire, rotation="without")
