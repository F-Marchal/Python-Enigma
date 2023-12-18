"""Provide an object that represent an Enigma machine (the german cypher machine).

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

from Rotor import Rotor
from Errors import RepeatedValueError, MissingValueError, NoRotorError, NoReflectorError
from ETW import ETW


class EnigmaMachine:
    """A class that represent the german WWII cipher machine Enigma.
    In order to work this machine need at least two rotors and a reflector.
    """

    def __init__(self, value_number: int = 26, translator: dict or list or tuple = None, description=None,
                 reflector: Rotor = None, etw: Rotor = None):
        if not isinstance(value_number, int) or value_number <= 1:
            raise ValueError(f"The number of value should be an integer greater than 1. Current <value_number> : "
                             f"{value_number}")

        self._length = value_number
        self._translator = {}
        self._reversed_translator = {}
        self._plugboard = {}
        self.translator = translator if translator is not None else []
        self._rotors: list[Rotor] = []
        self.description = description

        self._reflector = None
        self.set_reflector(reflector)
        self._etw = None
        self.set_etw(etw)

    def __str__(self):
        if isinstance(self.description, str):
            return self.description
        return super().__str__()

    def encode(self, value, translate_output: bool = True, is_a_decoding=False):
        """Do the full process of encoding (or decoding). Return an iterator.
        :param value:                  Values that you want to encode. Could be values in the translator or integer
                                            greater or equal to o and greater than <self.length>
        :param bool is_a_decoding:      Only if you use a Rotor instead of a Reflector as <self.reflector>.
                                           Specify if you want to decode or encode values.
        :param bool translate_output:   Do yield items are translated using machine's translator.
        :return iterator: All values after a pass inside the machine.
        """
        # Encoding preparation
        if len(self._rotors) <= 0:
            raise NoRotorError("No rotor load in this machine. Please load at least one rotor.")
        if self._reflector is None:
            raise NoReflectorError("No reflector load in this machine. Please load at least one reflector.")

        # Turn all rotor according to turnovers
        value = self.translate_in_integer(value)

        # Read plugboard
        value = self._read_plugboard(value)

        # Turn rotors
        self.turn()

        # read forward
        value = self._read_forward(value)

        # reflect value
        value = self._read_reflector(value, is_a_decoding)

        # read backward
        value = self._read_backward(value)

        # Read plugboard
        value = self._read_plugboard(value)

        # translation
        if translate_output:
            value = self.translate_number(value)

        return value

    def turn(self):
        """Turn rotors loaded inside this Machine.

        The order of rotors is defined by <self.get_non_stationary_items()>

        A rotor can turn when one of this condition is True:
            A) This rotor is the first in <self.get_non_stationary_items()>
            B) The last rotor has quit a turnover position (→ "last_rotor.turn() == True")
            C) All following condition are True:
                C-1) This rotor is on a turnover position (→ "rotor.is_in_turnover_position() == True")
                C-2) The last rotor has turned

        """
        item_that_can_turn = self.get_non_stationary_items()

        next_can_turn = True    # A) Condition
        for rotors in item_that_can_turn:
            if next_can_turn or rotors.is_in_turnover_position():  # A) and C-1) Condition
                next_can_turn = rotors.turn()  # B) and C-2) Condition

            if not next_can_turn:
                break

    def _read_forward(self, index: int) -> int:
        """scramble a value using all rotors. Correspond to how values are treat between the keyboard and the
        reflector.
        :param int index: an integer between 0 and <self.length>
        :return int: An index, ready to be used inside the reflector
        """
        index = self._etw.forward_reading(index)
        for rotors in self._rotors[::-1]:
            index = rotors.forward_reading(index)

        return index

    def read_forward(self, value, translate_result: bool = True):
        """scramble a value using all rotors. Correspond to how values are treat between the keyboard and the
        reflector.
        :param value: A value accepted by this machine.
        :param bool translate_result: Do the returned value is translated. If false, the value will be a number.
        :return: A value
        """
        index = self.translate_in_integer(value)
        index = self._read_forward(index)
        if translate_result:
            return self.translate_number(index)
        return index

    def _read_backward(self, index: int):
        """scramble a value using all rotors. Correspond to how values are treat between the reflector and the
        light bulb panel.
        :param index: an integer between 0 and <self.length>
        :return int: A new index, ready to be printed.
        """
        for rotors in self._rotors:
            index = rotors.backward_reading(index)
        index = self._etw.backward_reading(index)
        return index

    def read_backward(self, value, translate_result: bool = True):
        """scramble a value using all rotors. Correspond to how values are treat between the reflector and the
        light bulb panel.
        :param value: A value accepted by this machine.
        :param bool translate_result: Do the returned value is translated. If false, the value will be a number.
        :return: A value
        """
        index = self.translate_in_integer(value)
        index = self._read_backward(index)
        if translate_result:
            return self.translate_number(index)
        return index

    def _read_reflector(self, index: int, is_a_decoding: bool = False):
        """Pass an index inside the reflector.
        :param int index: An index accepted by this machine.
        :param bool is_a_decoding: Precise if this reading is a decoding or an encoding. This only matter when
                                    <self.reflector> is not a reflector.
        :return int: The output of the reflector
        """
        if is_a_decoding:
            return self._reflector.backward_reading(index)
        return self._reflector.forward_reading(index)

    def read_reflector(self,  value, translate_result: bool = True, is_a_decoding: bool = False):
        """Pass an index inside the reflector.
        :param value: A value accepted by this machine.
        :param bool translate_result: Do the returned value is translated. If false, the value will be a number.
        :param bool is_a_decoding: Precise if this reading is a decoding or an encoding. This only matter when
                                    <self.reflector> is not a reflector.
        :return int: The output of the reflector.
        """
        index = self.translate_in_integer(value)
        index = self._read_reflector(index, is_a_decoding)
        if translate_result:
            return self.translate_number(index)
        return index

    # Rotor management
    def clear_rotor(self):
        """Remove all rotors from the list of rotors loaded."""
        self._rotors.clear()

    def load_rotor(self, rotor: Rotor):
        """Add a rotor at the end of the rotor list."""
        if not isinstance(rotor, Rotor):
            raise TypeError(f"Rotor type expected : Got {type(rotor)}")
        elif rotor in self._rotors:
            raise KeyError(f"{rotor} is already loaded.")
        elif not self.is_compatible(rotor):
            raise ValueError(f"Incompatible rotor ({rotor}) : rotor length ({rotor.length}) != machine "
                             f"length {self._length}")
        self._rotors.append(rotor)

    def remove_rotor(self, rotor: Rotor or int):
        """Unload the rotor <rotor> or present at the index represent by <rotor>"""
        index = self._rotor_index_finder(rotor)
        del self._rotors[index]

    def displace_rotor(self, rotor_index: Rotor or int, to: Rotor or int):
        """Invert the position of two rotors.
        :param Rotor, int rotor_index: First Rotor that will be displaced. You can use its position in the rotor load.
        :param  Rotor, int to: Second Rotor that will be displaced. You can use its position in the rotor load.
        """
        rotor_index = self._rotor_index_finder(rotor_index)
        to = self._rotor_index_finder(to)
        self._rotors[rotor_index], self._rotors[to] = (self._rotors[to], self._rotors[rotor_index])

    def set_rotor_position(self, rotor: Rotor or int or str, position):
        """Modify the position of a Rotor. The position should be respect machine's length.
        :param Rotor, int, str rotor:  A rotor or its index / name (see <self.get_rotor>)
        :param position: A value or a number that represent the position.
        """
        if not isinstance(rotor, Rotor):
            rotor = self.get_rotor(rotor)
        rotor.position = self.translate_in_integer(position)

    def set_rotor_offset(self, rotor: Rotor or int or str, offset):
        """Modify the offset of a Rotor. The offset should be respect machine's length.
        :param Rotor, int, str rotor:  A rotor or its index / name (see <self.get_rotor>)
        :param offset: A value or a number that represent the offset.
        """
        if not isinstance(rotor, Rotor):
            rotor = self.get_rotor(rotor)
        rotor.offset = self.translate_in_integer(offset)

    def get_rotor_position(self, rotor: Rotor or int or str):
        """Read the position of a Rotor and translated it. The position should be respect machine's length.
        :param Rotor, int, str rotor:  A rotor or its index / name (see <self.get_rotor>)
        :return: The position of this rotor translated by this machine.
        """
        if not isinstance(rotor, Rotor):
            rotor = self.get_rotor(rotor)
        return self.translate_number(rotor.position)

    def get_rotor_offset(self, rotor: Rotor or int or str):
        """Read the offset of a Rotor and translated it. The offset should be respect machine's length.
        :param Rotor, int, str rotor:  A rotor or its index / name (see <self.get_rotor>)
        :return: The offset of this rotor translated by this machine.
        """
        if not isinstance(rotor, Rotor):
            rotor = self.get_rotor(rotor)
        return self.translate_number(rotor.offset)

    def get_rotor(self, rotor: int or str) -> Rotor:
        """Find an element loaded inside this machine using its standard name or its index.
        :param int, str rotor: int : The index of this rotor.
                               str : "reflector", "ukw" for the reflector
                                     "etw", "entry wells" for the ETW
        :return Rotor: A rotor / an ETW / a Reflector
        """
        if isinstance(rotor, int):
            rotor = self._rotors[self._rotor_index_finder(rotor)]
            
        elif isinstance(rotor, str):
            if rotor.lower() in ("reflector", "ukw"):
                rotor = self._reflector
                if rotor is None:
                    raise NoReflectorError("Missing reflector")
    
            elif rotor.lower() in ("etw", "entry wells"):
                rotor = self._etw
    
            else:
                raise ValueError(f'"reflector", "ukw", "etw" or "entry wells" expected. Got : "{rotor}"')
    
        else:
            raise TypeError(f"int or str expected. got : '{type(rotor)}' ('{rotor}')")
        return rotor

    def index_rotor(self, rotor: Rotor) -> int:
        """Index a rotor inside this machine.
        :param rotor rotor: A Rotor loaded inside this machine.
        :return int: The index of this Rotor.
        """
        return self._rotors.index(rotor)

    def _rotor_index_finder(self, rotor_index: int or Rotor) -> int:
        """Internal function. Take an index / a Rotor and return an index that correspond to this Rotor.
        :param int or Rotor rotor_index: positive or negative integer or Rotor.
        :return: Index a rotor using the Rotor or an integer (positive or negative)
        """
        # Some verifications
        if isinstance(rotor_index, Rotor):
            rotor_index = self.index_rotor(rotor_index)
        elif not isinstance(rotor_index, int):
            raise TypeError(f"Int or Rotor expected : Got {type(rotor_index)}")
            
        # Index computation
        if rotor_index < 0:
            rotor_index = len(self._rotors) - rotor_index
        if not 0 <= rotor_index < len(self._rotors):
            raise ValueError(f"Int between 0 and {len(self._rotors) - 1} expected. Got {rotor_index}")

        return rotor_index

    def get_non_stationary_items(self) -> list[Rotor]:
        """Give a list of object loaded into this machine (Reflector, ETW, Rotors) that are allowed to turn.
        :return list: List of Reflector / ETW / Rotors that are allowed to turn. They are in the correct order
        to be used by <self.turn>."""
        initial_list = [self._etw, *self._rotors[::-1], self._reflector] if self._reflector else self._rotors
        return [item for item in initial_list if item.can_rotate()]

    def get_stationary_items(self) -> list[Rotor]:
        """Give a list of object loaded into this machine (Reflector, ETW, Rotors) that are not allowed to turn.
        :return list: List of Reflector / ETW / Rotors that are not allowed to turn."""
        initial_list = [self._etw, *self._rotors[::-1], self._reflector] if self._reflector else self._rotors
        return [item for item in initial_list if not item.can_rotate()]
    
    # Reflector 
    def set_reflector(self, reflector: Rotor):
        """:param Rotor reflector: The Object that will be used as a reflector.
         Note that if <reflector> is not a Reflector, you will have to precise if you are doing an 
         encoding or a decoding."""
        if reflector is None:
            pass
        elif not self.is_compatible(reflector):
            raise ValueError(f"Incompatible rotor ({reflector}) : rotor length ({reflector.length}) != machine "
                             f"length {self._length}")

        self._reflector = reflector
        
    @property
    def reflector(self) -> Rotor:
        """:return Rotor: The Object used as an entry wheel."""
        return self._reflector

    @reflector.setter
    def reflector(self, value: Rotor):
        """:param Rotor value: The Object that will be used as a reflector.
        See <self.set_reflector>."""
        self.set_reflector(value)
        
    # ETW
    def set_etw(self, etw: Rotor):
        """Modify the current etw.
        :param Rotor etw: An Object that will be used as an entry wheel."""
        if etw is None:
            etw = ETW(wire=tuple(range(0, self._length)))
        if not self.is_compatible(etw):
            raise ValueError(f"Incompatible rotor ({etw}) : rotor length ({etw.length}) != machine "
                             f"length {self._length}")
        self._etw = etw
    
    @property
    def etw(self) -> Rotor:
        """:return Rotor: The Object used as an entry wheel."""
        return self._etw

    @etw.setter
    def etw(self, value: Rotor):
        """:param Rotor value: The Object that will be used as an entry wheel.
        See <self.set_etw>."""
        self.set_etw(value)
        
    # Plugboard
    def plug(self, first_value, second_value, *others_values):
        """This function allow the permutation of two values (as Enigma's plugboard would be).
        first_value and second_value are swapped during the output / input phase of an encoding.
        With first_value=0 and second_value=1, when 0 is input / output, the machine encode a 1 and vis versa.

        :param first_value:     A value that will be swapped with <second_value>
        :param second_value:    A value that will be swapped with <first_value>
        :param others_values:   A number of other values to swap. (Will call this function again for each couple).

        Values passed inside this function are translated using <self.translate_in_integer>

        :raise KeyError: When <first_value> or <second_value> is already swapped with another value.
        """
        # Pass <others_values> inside this function.
        if others_values:
            self.plug(*others_values)

        # Translate values
        first_value = self.translate_in_integer(first_value)
        second_value = self.translate_in_integer(second_value)

        # None of this
        if self.is_plugged(first_value):
            if self._plugboard[first_value] == second_value:
                # This couple already exist, let say there is no need to raise an error.
                return
            raise KeyError(f"{first_value} ({self.translate_number(first_value)}) is already inside the plugboard.")
        if self.is_plugged(second_value):
            raise KeyError(f"{second_value} ({self.translate_number(second_value)}) is already inside the plugboard.")

        # Save the modifications
        self._plugboard[first_value] = second_value
        self._plugboard[second_value] = first_value

    def unplug(self, value, *others_values):
        """This function remove the permutation between two values.
        value (and the other value swapped with <value>) will no longer be
        swapped during the output / input phase of an encoding.

        :param value:           The value that will not be swapped anymore.
        :param others_values:   A number of other values (Will call this function again for each value).

        Values passed inside this function are translated using <self.translate_in_integer>
        """
        # Pass <others_values> inside this function.
        if others_values:
            self.unplug(*others_values)

        # Translate value
        first_value = self.translate_in_integer(value)

        # No need to unplug value that isn't plug.
        if not self.is_plugged(first_value):
            return

        # Remove <first_value> and the value that is swapped with <first_value> from the plugboard.
        second_value = self._plugboard[first_value]
        del self._plugboard[first_value]
        del self._plugboard[second_value]

    def is_plugged(self, value) -> bool:
        """:return bool: Do this value is swapped with another value inside the plugboard ?
         Values passed inside this function are translated using <self.translate_in_integer>."""
        value = self.translate_in_integer(value)
        return value in self._plugboard

    def _read_plugboard(self, index: int) -> int:
        """Internal function.
        Use the plugboard to swap indexes.
        :param int index: An index that can be used by this Machine.
        :return int: The result of the permutation due to the plugboard."""
        if index in self._plugboard:
            return self._plugboard[index]
        return index

    def read_plugboard(self, value, translate_result: bool = True):
        """Read the plugboard and return the value that is swapped with <value>
        :param value:   A value that can be translated by this machine or an integer.
        :param bool translate_result: Do the result of the permutation is translated ?
        """
        plug_result = self._read_plugboard(self.translate_in_integer(value))
        if translate_result:
            return self.translate_number(plug_result)
        return value

    @property
    def plugboard(self) -> dict[int:int]:
        """:return dict: a copy of the plugboard."""
        return self._plugboard.copy()

    # translator management
    def set_translator(self, translator: dict or list or tuple):
        """Define a way to translate values from rotors (int) to other values (str for example)
        /!\\ It's highly recommended to avoid to translate values from rotors intoo values that rotors can return
            (meaning to use integer between 0 and <self.length>).
        A <translator> is a dict that respect the following rules:
            A: All keys has to be greater or equal than 0 and lower than <self.length>.
            B: All possible keys has to be inside
            C: All values has to be unique

        If <translator> is a list or a tuple:
            A: <translator> length has to be lower or equal to <self.length>
            B: each values inside <translator> has to be unique
        """
        # --- --- Type verifications --- ---
        if isinstance(translator, str):
            translator = list(translator)

        if isinstance(translator, (list, tuple)):
            if len(set(translator)) != len(translator):
                # Assure that <translator>'s values are unique.
                repetitions = [values for values in translator if translator.count(values) != 1]
                raise RepeatedValueError(repetitions, f"Some values inside <translator> are repeated : "
                                         f"{repetitions}")

            # Fill missing values inside <translator> to assure that len(translator) >= self._length.
            translator_length = len(translator)
            if len(translator) < self._length:
                translator = list(translator) + list(range(translator_length, self._length))

            # Transform <translator> into a dictionary
            translator = {i: value for i, value in enumerate(translator)}

        elif not isinstance(translator, dict):
            # Assure that <translator> is a dict or a list or a tuple.
            raise TypeError(f"<translator> should be  dict or list or tuple. Got : {type(translator)}")

        elif len(set(translator.values())) != len(translator.values()):
            # Assure that <translator>'s values are unique.
            values = list(translator.values())
            repetitions = [val for val in values if values.count(val) != 1]
            raise RepeatedValueError(repetitions, f"Some values inside <translator.values> are repeated : "
                                     f"{repetitions}")

        #
        # --- --- Normal translator --- ---
        # Assure that the correct number of values are inside <translator>
        if len(translator) != self._length:
            raise IndexError(f"{self._length} different keys expected inside <translator>. "
                             f"Got : {len(translator)}")

        # Assure that no values are missing.
        # All values from 0 to <self._length> (not include) should be inside the translator
        missing_values = set(range(0, self._length)).difference(translator)
        if missing_values:
            raise MissingValueError(missing_values, f"{len(missing_values)} are missing inside <translator> "
                                    f": {missing_values}")

        # --- --- Save --- ---
        self._translator = translator
        self._reversed_translator = {value: key for key, value in translator.items()}

    def is_translated(self, value) -> bool:
        """:return bool: Does a <value> can be translated by this machine."""
        return value in self._reversed_translator

    def translate_number(self, number: int):
        """Turn a number (integer) into another value using <self.translator>"""
        return self._translator[number]

    def translate_item(self, item) -> int:
        """Turn an item (any) into another value using <self.reversed_translator>"""
        return self._reversed_translator[item]

    def translate_in_integer(self, value) -> int:
        """Turn a <value> intoo an integer:
        :return int: an index that can be used by this Machine and that correspond to <value>"""
        if self.is_translated(value):
            return self.translate_item(value)
        elif self.is_in_range(value):
            return value
        else:
            raise ValueError(f"Integer greater or equal to 0 and lower than {self._length} or value inside"
                             f"translator expected. Got : {value}")

    @property
    def translator(self) -> dict:
        """A dict that say how integer are translated in other value."""
        return self._translator.copy()

    @translator.setter
    def translator(self, value):
        """:param value: A dict that say how integer are translated in other value.
        See <self.set_translator>"""
        self.set_translator(value)

    @property
    def reversed_translator(self) -> dict:
        """A dict that say how items are translated in integer."""
        return self._reversed_translator.copy()
        
    # Others
    def is_in_range(self, value: int) -> bool:
        """Do a <value> is an integer that can be used by this machine."""
        return isinstance(value, int) and 0 <= value < self._length

    def is_compatible(self, rotor: Rotor) -> bool:
        """Do a <rotor> can be used by this machine."""
        return isinstance(rotor, Rotor) and rotor.length == self._length

    def get_key(self, reflector: bool = None, etw: bool = None, offset: bool = False) -> list:
        """return a list of (translated) positions. By default, Reflector and ETW are not included.
        :param bool reflector:  Do Reflector position in included inside the list
        :param bool etw:  Do ETW position in included inside the list
        :param bool offset:     If True, this function will return offset instead of positions.
        :return list: a list of (translated) positions. [reflector, *rotors, ETW]
        """
        # Find if we will get position or offset
        command = self.get_rotor_position
        if offset:
            command = self.get_rotor_offset

        # Create a list of potion / offset
        result = [command(rotor) for rotor in self._rotors]

        # Add reflector or offset at the correct place in the list
        if reflector:
            result = [command("UKW"), *result]
        if etw:
            result.append(command("ETW"))

        return result

    def set_key(self, *values, reflector=None, etw=None, offset: bool = False):
        """Set all positions using a list of positions. By default, Reflector and ETW are not included.
        :param bool reflector:  Do Reflector position in included inside the list
        :param bool etw:  Do ETW position in included inside the list
        :param bool offset:     If True, this function will set offset instead of positions.
        List order : [reflector, *rotors, ETW]
        """
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = values[0]

        # List all concerned objects.
        items = self._rotors
        if reflector:
            items = [self.get_rotor("UKW"), *items]
        if etw:
            items.append(self.get_rotor("ETW"))

        if len(values) < len(items):
            raise ValueError(f'Not enough values. {len(values)} received on the {len(items)} expected')

        # find the right command
        command = self.set_rotor_position
        if offset:
            command = self.set_rotor_offset

        # Set all positions
        for i, rotor in enumerate(items):
            command(rotor, values[i])

    @property
    def length(self) -> int:
        """How many values are inside machine's Rotors."""
        return self._length

    @property
    def description(self):
        """A description of this Machine. Generally contain historical or usage information."""
        return self._description

    @description.setter
    def description(self, value):
        """A description of this Machine. Generally historical or usage information."""
        self._description = value
