# A TESTER : PlugBoard, Encoding
# A AJOUTER : Properties
# A AJOUTER : fast_encode

import timeit
from Rotor import Rotor
from Errors import RepeatedValueError, MissingValueError, NoRotorError, NoReflectorError

class EnigmaMachine:
    def __init__(self, value_number: int = 26, translator: dict or list or tuple = None):
        if not isinstance(value_number, int) or value_number <= 1:
            raise ValueError(f"The number of value should be an integer greater than 1. Current <value_number> : "
                             f"{value_number}")

        self._length = value_number
        self._translator = {}
        self._reversed_translator = {}
        self._plugboard = {}
        self.translator = translator if translator is not None else []

        self._rotors: list[Rotor] = []
        self._reflector = None

    # cryptographic related methods
    def encode(self, *values, is_a_decoding=False, translate_output: bool = True) -> iter:
        """Do the full process of encoding (or decoding). Return an iterator.
        :param values:                  Values that you want to encode. Could be values in the translator or integer
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

        for value in values:
            # Turn all rotor according to notches
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

            yield value

    def _read_plugboard(self, index: int):
        if index in self._plugboard:
            return self._plugboard[index]
        return index

    def read_plugboard(self, value, translate_result: bool = True):
        plug_result = self._read_plugboard(self.translate_in_integer(value))
        if translate_result:
            return self.translate_number(plug_result)
        return value

    def turn(self):
        i = 0
        item_that_can_turn = self.get_non_stationary_items()
        item_number = len(item_that_can_turn)
        while i < item_number and item_that_can_turn[i].turn():
            i += 1

    def _read_forward(self, index: int):
        for rotors in self._rotors[::-1]:
            index = rotors.forward_reading(index)
        return index

    def read_forward(self, value, translate_result: bool = True):
        index = self.translate_in_integer(value)
        index = self._read_forward(index)
        if translate_result:
            return self.translate_number(index)
        return index

    def _read_backward(self, index: int):
        for rotors in self._rotors:
            index = rotors.backward_reading(index)
        return index

    def read_backward(self, value, translate_result: bool = True):
        index = self.translate_in_integer(value)
        index = self._read_backward(index)
        if translate_result:
            return self.translate_number(index)
        return index

    def _read_reflector(self, index: int, is_a_decoding: bool = False):
        if is_a_decoding:
            return self._reflector.backward_reading(index)
        return self._reflector.forward_reading(index)

    def read_reflector(self,  value, translate_result: bool = True, is_a_decoding: bool = False):
        index = self.translate_in_integer(value)
        index = self._read_reflector(index, is_a_decoding)
        if translate_result:
            return self.translate_number(index)
        return index

    def read_value(self, value, translate_result: bool = True, is_a_decoding: bool = False):
        index = self.translate_in_integer(value)

        # read forward
        index = self._read_forward(index)

        # reflect value
        index = self._read_reflector(index, is_a_decoding)

        # read backward
        index = self._read_backward(index)

        if translate_result:
            return self.translate_number(index)
        return index

    # Rotor management
    def clear_rotor(self):
        self._rotors.clear()

    def load_rotor(self, rotor: Rotor):
        if not isinstance(rotor, Rotor):
            raise TypeError(f"Rotor type expected : Got {type(rotor)}")
        elif rotor in self._rotors:
            raise KeyError(f"{rotor} is already loaded.")
        self._rotors.append(rotor)

    def remove_rotor(self, rotor: Rotor or int):
        index = self._rotor_index_finder(rotor)
        del self._rotors[index]

    def displace_rotor(self, rotor_index: Rotor or int, to: Rotor or int):
        rotor_index = self._rotor_index_finder(rotor_index)
        to = self._rotor_index_finder(to)
        self._rotors[rotor_index], self._rotors[to] = (self._rotors[to], self._rotors[rotor_index])

    def get_rotor(self, index: int) -> Rotor:
        return self._rotors[index]

    def index_rotor(self, rotor) -> int:
        return self._rotors.index(rotor)

    def set_reflector(self, reflector: Rotor):
        self._reflector = reflector

    def _rotor_index_finder(self, rotor_index: int or Rotor):
        if isinstance(rotor_index, Rotor):
            rotor_index = self.index_rotor(rotor_index)

        elif not isinstance(rotor_index, int):
            raise TypeError(f"Int or Rotor expected : Got {type(rotor_index)}")

        if rotor_index < 0:
            rotor_index = len(self._rotors) - rotor_index

        if not 0 <= rotor_index < len(self._rotors):
            raise ValueError(f"Int between 0 and {len(self._rotors) - 1} expected. Got {rotor_index}")

        return rotor_index

    def get_non_stationary_items(self):
        initial_list = [*self._rotors, self._reflector] if self._reflector else self._rotors
        return [item for item in initial_list if item.can_rotate()]

    def get_stationary_items(self):
        initial_list = [*self._rotors, self._reflector] if self._reflector else self._rotors
        return [item for item in initial_list if not item.can_rotate()]

    # Plugboard
    def plug(self, first_value, second_value, *others_values):
        if others_values:
            self.plug(*others_values)

        first_value = self.translate_in_integer(first_value)
        second_value = self.translate_in_integer(second_value)

        if self.is_plug(first_value):
            raise KeyError(f"{first_value} ({self.translate_number(first_value)}) is already inside the plugboard.")
        if self.is_plug(second_value):
            raise KeyError(f"{second_value} ({self.translate_number(second_value)}) is already inside the plugboard.")

        self._plugboard[first_value] = second_value
        self._plugboard[second_value] = first_value

    def unplug(self, first_value, second_value, *others_values):
        if others_values:
            self.unplug(*others_values)

        first_value = self.translate_in_integer(first_value)
        second_value = self.translate_in_integer(second_value)

        if not self.is_plug(first_value):
            raise KeyError(f"{first_value} ({self.translate_number(first_value)}) is not inside the plugboard.")
        if not self.is_plug(second_value):
            raise KeyError(f"{second_value} ({self.translate_number(second_value)}) is not inside the plugboard.")

        del self._plugboard[first_value]
        del self._plugboard[second_value]


    def is_plug(self, value) -> bool:
        value = self.translate_in_integer(value)
        return value in self._plugboard

    @property
    def plugboard(self):
        return self._plugboard.copy()

    # translator management
    def set_translator(self, translator: dict or list or tuple):
        """Define a way to translate values from rotors (int) to other values (str for example)
        /!\\ It's highly recommended to avoid to translate values from rotors intoo values that rotors can return
            (meaning integer between 0 and <self.length>).
         A <translator> is a dict that respect the following rules:
            A: All keys has to be greater or equal than 0 and lower than <self.length>.
            B: All possible keys has to be inside
            C: All values has to be unique

        If <translator> is a list or a tuple:
            A: <translator> length has to be lower or equal to <self.length>
            B: each values inside <translator> has to be unique
        """
        # --- --- Type verifications --- ---
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
        if self.is_translated(value):
            return self.translate_item(value)
        elif self.is_in_range(value):
            return value
        else:
            raise ValueError(f"Integer greater or equal to 0 and lower than {self._length} or value inside"
                             f"translator expected. Got : {value}")

    # Others
    def is_in_range(self, value: int) -> bool:
        """Do a <value> is an integer that can be used by this machine."""
        return isinstance(value, int) and 0 <= value < self._length

    @property
    def length(self) -> int:
        """How many values are inside machine's Rotors."""
        return self._length

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

if __name__ == '__main__':
    EM = EnigmaMachine(4, translator={
        0: "a",
        1: "b",
        2: "d",
        3: "c",

    })

    R3 = Rotor({
        0: 1,
        1: 2,
        2: 3,
        3: 0,
    })
    R2 = Rotor({
        2: 1,
        1: 2,
        0: 3,
        3: 0,
    })
    R1 = Rotor({
        0: 1,
        3: 2,
        2: 3,
        1: 0,
    })
    EM.load_rotor(R1)
    EM.load_rotor(R2)
    EM.load_rotor(R3)
    print(EM._rotors)
    EM.remove_rotor(R3)
    print(EM._rotors)