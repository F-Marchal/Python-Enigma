"""


https://www.cryptool.org/en/cto/enigma-step-by-step
"""
# A AJOUTER : fast_encode

import timeit
from Rotor import Rotor
from Errors import RepeatedValueError, MissingValueError, NoRotorError, NoReflectorError
from ETW import ETW


class EnigmaMachine:
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

    def _read_forward(self, index: int):
        index = self._etw.forward_reading(index)
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
        index = self._etw.backward_reading(index)
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

        # PlugBoard
        index = self._read_plugboard(index)

        # read forward
        index = self._read_forward(index)

        # reflect value
        index = self._read_reflector(index, is_a_decoding)

        # read backward
        index = self._read_backward(index)

        # PlugBoard
        index = self._read_plugboard(index)

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


if __name__ == '__main__':
    import Historical
    EM3 = Historical.EnigmaG312.getEnigmaG31()
    abc = Historical.EnigmaG312.getAlphabet()
    print({abc[key]: abc[item] for key, item in Historical.EnigmaG312.getETW().wire.items()})
    r = ""
    o = 0
    for i in "OPREMIPSUMDOLORSITAMETCONSECTETURADIPISCINGELITPRAESENTETEROSVELNEQUESUSCIPITHENDRERITMAECENASLOREMFELISVIVERRAATELLUSSEDSCELERISQUELAOREETLIGULASUSPENDISSEMINISIVEHICULAAVEHICULAPORTATEMPUSEUQUAMNULLAUTPULVINARIPSUMCRASNECCONSECTETURLEOMORBIALIQUAMETVELITUTCONGUEPROINUTIPSUMLEONUNCRHONCUSORCIUTPELLENTESQUEMALESUADALEOENIMVOLUTPATEXNECPRETIUMNISIDIAMTEMPUSLOREMPELLENTESQUEQUISBIBENDUMMAGNAAENEANANTELOREMAUCTORATPULVINARINVIVERRAATELLUSPELLENTESQUEERATMAGNAFERMENTUMQUISLIGULAVITAESOLLICITUDINDIGNISSIMTELLUSDONECSITAMETSEMVITAEODIOEGESTASALIQUAMPRAESENTUTEGESTASTELLUSAENEANSAGITTISMAGNAVELITSITAMETVULPUTATEELITALIQUAMEUQUISQUETEMPUSMAURISVITAEDUIPLACERATATEMPUSEXEUISMODQUISQUEAFELISIDEXFACILISISEGESTASASITAMETMIAENEANINCONVALLISNISINECPORTAURNAMAECENASEGETNISLUTLOREMCONDIMENTUMPRETIUMSEDPLACERATNUNCACEFFICITURHENDRERITNISIERATCONSEQUATELITTINCIDUNTSAGITTISDIAMDOLORSEDLACUSNAMMAGNAMETUSPULVINAREGETRISUSSITAMETFERMENTUMPOSUEREORCIINTEGERPLACERATTINCIDUNTORCIPULVINARULLAMCORPERSEDAVENENATISNUNCVESTIBULUMNECGRAVIDADOLORFEUGIATCURSUSNEQUESEDSEDPORTALACUSALIQUAMERATVOLUTPATSUSPENDISSEALIQUAMULTRICESLOREMNECDAPIBUSNUNCTEMPORATNUNCVENENATISLOREMLACUSSEDULLAMCORPERSEMCONGUEEUVESTIBULUMANTEIPSUMPRIMISINFAUCIBUSORCILUCTUSETULTRICESPOSUERECUBILIACURAEMORBIEGETCONDIMENTUMLACUSQUISTINCIDUNTMAURISVIVAMUSHENDRERITNULLASITAMETSAPIENVOLUTPATEUBLANDITTURPISRUTRUMINTERDUMETMALESUADAFAMESACANTEIPSUMPRIMISINFAUCIBUSPROINSOLLICITUDINRISUSNECFACILISISCONVALLISPELLENTESQUEHABITANTMORBITRISTIQUESENECTUSETNETUSETMALESUADAFAMESACTURPISEGESTASINPOSUERELIBEROUTFAUCIBUSTEMPUSEXNIBHIMPERDIETERATLAOREETPRETIUMNUNCODIOFACILISISMAGNANUNCFACILISISEXEGETDOLORMOLLISETEUISMODURNATINCIDUNTALIQUAMELEIFENDTORTORETMAURISPELLENTESQUENONCOMMODOLACUSFAUCIBUSVESTIBULUMATMALESUADAANTEALIQUAMJUSTOURNAPLACERATEUPURUSATCOMMODOPHARETRAORCIMAURISSEDIPSUMSITAMETMETUSCONGUEFRINGILLAINETEXSEDPELLENTESQUECONVALLISLEOUTMALESUADADONECCONSECTETURLECTUSSEDRUTRUMIMPERDIETMAURISESTORNAREJUSTOATCONSEQUATLIGULAMAGNAVELNULLAINMAURISMAGNAPULVINARNONMAURISEUSODALESVULPUTATENULLADONECEUELITEROSVESTIBULUMLUCTUSEROSLACUSNECMATTISMASSADIGNISSIMNECCLASSAPTENTTACITISOCIOSQUADLITORATORQUENTPERCONUBIANOSTRAPERINCEPTOSHIMENAEOSMAECENASETTINCIDUNTANTEFACILISISFERMENTUMJUSTOINTEGERMALESUADATORTORINANTETEMPORTINCIDUNTAENEANVENENATISTELLUSETLUCTUSSAGITTISDUIELITMAXIMUSRISUSEGETPOSUEREEXLACUSETSEMSUSPENDISSEUTPELLENTESQUEMETUSINLACINIATURPISLOREMNECPELLENTESQUELEOGRAVIDAVELSEDEGETANTEINDUIELEMENTUMINTERDUMVESTIBULUMIDLOREMORCINULLAMMAXIMUSULLAMCORPERDOLOREGETEFFICITURMASSAMOLESTIEETNULLAIMPERDIETALIQUETODIOSEDHENDRERITVELITFACILISISSITAMETSUSPENDISSENECMIQUISORCIGRAVIDAFERMENTUMVIVAMUSVITAEBIBENDUMTELLUSSEDELEIFENDLIBERONONLOREMMAXIMUSACTINCIDUNTLEOPORTTITORINTEGERSEDDUIMETUSVIVAMUSQUISLUCTUSLACUSVIVAMUSRHONCUSTORTORATTORTORLUCTUSNONTEMPORSAPIENVEHICULANULLAMMAGNANEQUEEUISMODATSAGITTISACSOLLICITUDINATIPSUMSEDVITAESEMALIQUAMERATMAXIMUSCONSEQUATEUANISIDUISINMOLESTIEENIMEGETLUCTUSMIINTEGEREUSAGITTISLECTUSMAURISVELTORTORQUISDOLORVIVERRAVOLUTPATDUISDIGNISSIMURNAQUISTINCIDUNTPELLENTESQUEAENEANACCUMSANETVELITEUPELLENTESQUEDUISFELISDOLORSCELERISQUEVITAEELITTINCIDUNTALIQUAMINTERDUMSAPIENVIVAMUSAUCTORVITAENEQUEVITAESAGITTISQUISQUEEGETIPSUMMASSADUISUTNIBHIDESTTINCIDUNTULTRICIESACNONVELITMAECENASATLOREMDICTUMFRINGILLAMAGNANECFAUCIBUSNISIVIVAMUSEXNULLASEMPERETLEOQUISVEHICULAVESTIBULUMMAGNASEDBLANDITBIBENDUMMASSANONSODALESMAURISULLAMCORPERBIBENDUMNULLAETPHARETRAQUISQUEEXVELITTRISTIQUEEUIPSUMACONVALLISBLANDITNISIPHASELLUSNULLAQUAMLOBORTISEUCOMMODOAVEHICULAACANTEINTEGERULTRICESFACILISISPORTAINVULPUTATEMOLESTIEPURUSSEDFRINGILLAFUSCEULTRICESDIGNISSIMNULLANONFERMENTUMJUSTOCONDIMENTUMACDONECCONSEQUATTURPISSEDLACUSPORTANECPOSUEREELITVIVERRASEDQUISCOMMODODUIDONECLACINIAVELITUTAUGUECONSECTETURVULPUTATEPELLENTESQUEEGESTASULLAMCORPERORNAREORCIVARIUSNATOQUEPENATIBUSETMAGNISDISPARTURIENTMONTESNASCETURRIDICULUSMUSINTEGERCONSEQUATLACUSUTFEUGIATULTRICESNULLAAUGUEFEUGIATMETUSNECTEMPORNISLQUAMANULLANUNCINTERDUMMAURISSITAMETJUSTOINTERDUMELEMENTUMCURABITURVESTIBULUMARCUINULLAMCORPERSOLLICITUDINNUNCPELLENTESQUEVESTIBULUMMAURISSOLLICITUDINDIGNISSIMTELLUSPORTTITORSITAMETMAECENASNECSOLLICITUDINAUGUEPELLENTESQUEFERMENTUMNEQUETRISTIQUEMIDAPIBUSUTIACULISDUIRHONCUSINULTRICESESTMIACONDIMENTUMERATMAXIMUSVELDONECCOMMODOSEDDOLORVITAELACINIAPRAESENTFERMENTUMRISUSQUISODIOVESTIBULUMQUISALIQUETVELITVARIUSPRAESENTMALESUADATINCIDUNTIPSUMATLUCTUSSEMVOLUTPATPORTTITORVESTIBULUMINVEHICULAVELITNONVESTIBULUMANTEDUISCONSEQUATENIMPURUSSOLLICITUDINCONSEQUATVELITPELLENTESQUEEUETIAMULLAMCORPERCONSEQUATENIMMOLLISACCUMSANNULLAMVENENATISEUISMODSAPIENACURSUSVELITMALESUADAACETIAMVARIUSAMASSAEGETPLACERATNAMTRISTIQUETELLUSENIMORNAREDAPIBUSFELISEFFICITURUTPELLENTESQUEVENENATISIACULISEROSUTPELLENTESQUESEDTELLUSESTORNARETEMPORSEMACGRAVIDACONVALLISNIBHCURABITURSEMPERJUSTONECCONVALLISINTERDUMTURPISFELISBIBENDUMARCUQUISSUSCIPITNEQUENIBHIDNEQUEETIAMAUCTORNUNCVELVESTIBULUMULTRICESDUISSCELERISQUEQUAMIDRISUSGRAVIDAIACULISPELLENTESQUECONSEQUATLOREMQUAMEUPORTTITORERATSCELERISQUEVELNULLAMUTANTECONSEQUATACCUMSANARCUATINCIDUNTARCUPHASELLUSQUISNISIPORTASODALESVELITVITAEULTRICIESODIOPELLENTESQUEFACILISISTEMPORJUSTOETRHONCUSPROINNUNCELITGRAVIDAUTMASSAULTRICESFRINGILLASODALESDOLORNULLAMSOLLICITUDINDOLORLOREMACULTRICIESANTEDICTUMACNULLAMFINIBUSIPSUMQUISNEQUEHENDRERITMOLLISPHASELLUSEFFICITURLACINIASAPIENVELEGESTASFUSCESITAMETAUCTORJUSTOCURABITURSEMDUIMOLESTIENECIMPERDIETAAUCTORINMAURISALIQUAMERATVOLUTPATPHASELLUSCONSECTETURNEQUELIGULASEDULTRICESLEOORNAREDIGNISSIMPRAESENTQUISMETUSVELMIDIGNISSIMULTRICIESNAMVIVERRAFELISNULLAEGETIMPERDIETODIOMAXIMUSQUISQUISQUEAALIQUAMMAURISNUNCNIBHLOREMHENDRERITFAUCIBUSLEOPOSUEREVEHICULAEUISMODLOREMORCIVARIUSNATOQUEPENATIBUSETMAGNISDISPARTURIENTMONTESNASCETURRIDICULUSMUSQUISQUESITAMETEGESTASLOREMQUISMALESUADANULLADONECTURPISVELITULTRICESVITAESCELERISQUEEGETCOMMODOEUMAURISCURABITURULLAMCORPERDIAMATULTRICESCOMMODONEQUEMAURISVEHICULAANTEEGETULTRICIESJUSTONEQUESEDTELLUSDONECDIGNISSIMIMPERDIETULLAMCORPERMORBIDICTUMDIAMFRINGILLAQUAMEGESTASCONSEQUATNAMAUGUENISISOLLICITUDINUTLIBEROETFEUGIATINTERDUMAUGUEPHASELLUSATODIOFRINGILLARHONCUSELITSEDSUSCIPITERATPHASELLUSACMAURISESTNULLAMCURSUSNIBHNECMAURISPLACERATALIQUETVIVAMUSULLAMCORPERVELITORNAREINTERDUMDOLORSITAMETVEHICULALOREMMAECENASINNEQUELIGULASUSPENDISSEPOTENTIMAURISEROSLIBEROSEMPERIDLAOREETVELIMPERDIETETLEOPHASELLUSINFRINGILLAODIOINVITAELACUSSITAMETSEMTEMPUSEUISMODSUSPENDISSEUTTINCIDUNTEROSINLUCTUSDIAMSEDVOLUTPATVESTIBULUMNUNCPORTTITORHENDRERITETIAMUTSAPIENACEROSULLAMCORPERBIBENDUMNULLAMMATTISARCUSEDPURUSVESTIBULUMACAUCTORMASSAVEHICULAMORBIDICTUMNISLVELQUAMFERMENTUMETFERMENTUMFELISPRETIUMSEDVITAEMAGNAAARCUVEHICULAULLAMCORPERAENEANMAGNAFELISSAGITTISVELTELLUSETSAGITTISVARIUSTURPISVESTIBULUMPOSUEREVEHICULAURNAIMPERDIETGRAVIDAVELITPORTAETFUSCEMOLESTIEDAPIBUSVIVERRACRASNISLARCUCONDIMENTUMNECACCUMSANQUISDAPIBUSINJUSTODUISVULPUTATEACCUMSANFELISDONECSITAMETMASSANONERATEFFICITURLACINIAETVITAELOREMNAMSEDELEMENTUMORCIEUPORTAMETUSPRAESENTLACUSMAGNAULTRICESVITAESEMNECCOMMODOCURSUSLEONULLASITAMETVELITNONNISIORNAREALIQUETINEGETMASSANULLAMALIQUETQUISRISUSVELALIQUETCURABITUREUEXMETUSQUISQUEVIVERRAEUISMODELITCONVALLISVEHICULAUTEGETLACUSETMICONDIMENTUMMOLLISETIAMAUCTORRISUSCOMMODOSAPIENMAXIMUSEULACINIATORTORVULPUTATEVESTIBULUMANTEIPSUMPRIMISINFAUCIBUSORCILUCTUSETULTRICESPOSUERECUBILIACURAECRASAMAGNAURNAPELLENTESQUEVARIUSNISIIDVIVERRATRISTIQUESAPIENARCUSAGITTISODIOVELPRETIUMLIBEROERATIDMAURISMAECENASSEDQUAMAENIMCONDIMENTUMDICTUMANONERATMAECENASVELELEMENTUMODIONUNCFRINGILLALIBEROACENIMCONDIMENTUMPHARETRAVELEGETERATMAURISINDIAMFEUGIATIMPERDIETLIGULAATAUCTORLOREMPROINFACILISISTURPISVITAESOLLICITUDINBLANDITURNAPURUSPORTALIBEROQUISMOLESTIELACUSARCUVELEXNULLAMVELTELLUSSAGITTISLOBORTISNULLANONBLANDITNULLAUTSEDPORTTITORLACUSVESTIBULUMIMPERDIETMASSAFELISSITAMETFERMENTUMSEMTINCIDUNTNONSEDUTLIGULAPURUSETIAMETLOBORTISENIMINBLANDITULTRICESLAOREETINESTLECTUSULLAMCORPERSEDLIGULABLANDITVEHICULAULTRICESMASSACRASULTRICIESAUGUEQUAMINULTRICIESARCUSCELERISQUEETINTERDUMETMALESUADAFAMESACANTEIPSUMPRIMISINFAUCIBUSNAMQUISEXVESTIBULUMELEIFENDSAPIENUTTINCIDUNTEROSUTEGESTASSEMARCUEUIMPERDIETERATTEMPORRUTRUMETIAMFAUCIBUSNISLEUNIBHTRISTIQUEIDALIQUAMEROSFERMENTUMMAURISALIQUAMAUGUEEUCONSECTETURSUSCIPITDUISNONQUAMNECEROSMOLESTIELAOREETAENEANERATTELLUSRUTRUMIDULTRICIESADAPIBUSUTFELISPHASELLUSHENDRERITPOSUEREEROSVELCONDIMENTUMTELLUSDIGNISSIMSEDCURABITURELEMENTUMDUIINMATTISFERMENTUMMAURISFEUGIATENIMACJUSTOALIQUETINTERDUMNULLAEGETHENDRERITFELISVIVAMUSGRAVIDAEXATVENENATISSCELERISQUEIPSUMAUGUESCELERISQUEVELITATVOLUTPATLIGULAARCUSEDDUIVIVAMUSAUCTORLEONECODIOVESTIBULUMPORTTITORCURABITURSAGITTISNISLIDACCUMSANELEMENTUMTURPISLIGULACONGUENIBHVELVESTIBULUMPURUSLIGULAPORTTITORMETUSDONECTEMPORAUGUEVITAEVENENATISSUSCIPITTELLUSMASSAULTRICESERATATAUCTORLACUSTORTORAEROSNAMSEDFINIBUSTORTORSEDDICTUMNULLAFUSCEELEMENTUMODIOFELISSEDELEIFENDEROSFRINGILLAETQUISQUESEDTEMPUSJUSTODONECVELHENDRERITDUIETEUISMODSEMCRASVOLUTPATEROSODIOEGETORNAREELITHENDRERITQUISINFEUGIATLIGULAQUISULLAMCORPERVIVERRANIBHNULLAEUISMODNISLETALIQUETSEMTELLUSAANTECURABITURVIVERRAFELISMIACEFFICITURODIOSAGITTISEGETNULLAALIQUETTELLUSSITAMETTEMPUSCONSEQUATNISIIPSUMPORTTITOREXQUISDIGNISSIMNIBHTORTORMOLESTIEMIVIVAMUSATQUAMSITAMETMETUSTINCIDUNTTINCIDUNTVITAEQUISLOREMNULLAMMETUSANTELACINIAUTTEMPUSACPELLENTESQUENECFELISPROINHENDRERITATMAURISQUISAUCTORVESTIBULUMVESTIBULUMDIAMACTINCIDUNTEFFICITURINTERDUMETMALESUADAFAMESACANTEIPSUMPRIMISINFAUCIBUSAENEANFACILISISCONSECTETURGRAVIDAMAURISULTRICIESORCIQUISLACUSULLAMCORPERSITAMETACCUMSANNUNCBIBENDUMNULLANULLAFELISALIQUAMUTULTRICIESSEDALIQUETETMETUSVIVAMUSVELITFELISCOMMODOINVELITATELEIFENDVIVERRAFELISCRASETMOLLISESTSEDPULVINARERATNONRUTRUMMAXIMUSMORBIIDMASSAELEMENTUMVEHICULASEMSODALESVENENATISODIOETIAMUTHENDRERITEROSSUSPENDISSELOREMNISIPULVINAREGETORCIUTCONGUERUTRUMORCISEDETEGESTASLIBEROPELLENTESQUEHABITANTMORBITRISTIQUESENECTUSETNETUSETMALESUADAFAMESACTURPISEGESTASMAURISALIQUETNIBHMAURISINEUISMODARCUTRISTIQUEVELVIVAMUSVELFINIBUSVELITALIQUAMEGETELEMENTUMMAGNAINHACHABITASSEPLATEADICTUMSTPELLENTESQUEMALESUADAVESTIBULUMTEMPORUTNONSEMEXNULLAMCONGUELACUSAODIOVOLUTPATINTEMPUSNUNCALIQUAMSUSPENDISSEPULVINARSOLLICITUDINLIGULAVITAEDAPIBUSDONECELEIFENDELEMENTUMNULLAACFAUCIBUSESTPOSUEREACNUNCORCIRISUSSEMPERNONEXVITAEPHARETRADIGNISSIMTORTORSEDEFFICITURAUCTORSEMPERMORBIQUISERATANIBHBLANDITVULPUTATEPRAESENTVARIUSVIVERRADICTUMAENEANDOLORLACUSVULPUTATEETURNAVITAEULTRICIESINTERDUMMASSAPROINACLIGULAEGETSEMSCELERISQUESODALESVITAEUTIPSUMPELLENTESQUEMAURISSEMEUISMODNONELEMENTUMATHENDRERITUTLEOPHASELLUSCONSECTETURORNARETINCIDUNTETIAMELEMENTUMNISIERATATRISTIQUELACUSTEMPORACMAURISEGETCONSEQUATANTEINTEGERIACULISVIVERRAIPSUMPELLENTESQUEHABITANTMORBITRISTIQUESENECTUSETNETUSETMALESUADAFAMESACTURPISEGESTASINTEGERPULVINARVULPUTATEULLAMCORPERSEDIDLIGULAQUISMAGNAVULPUTATEPLACERATPRAESENTEGETTEMPORDUIALIQUAMVARIUSANTESEDLACUSCURSUSALIQUETQUISQUEATNUNCEFFICITUREROSPRETIUMGRAVIDANECEUENIMVESTIBULUMFACILISISADIAMVELVULPUTATESUSPENDISSELUCTUSQUISMETUSETSCELERISQUENUNCIMPERDIETALIQUAMTEMPUSFUSCEUTACCUMSANMETUSSITAMETSUSCIPITVELITAENEANACCUMSANRISUSVELIPSUMMOLESTIENECMATTISTURPISTINCIDUNTINLOBORTISQUAMEGETULTRICESRUTRUMTORTORDOLORFERMENTUMQUAMVELEUISMODLACUSRISUSETMIVESTIBULUMANTEIPSUMPRIMISINFAUCIBUSORCILUCTUSETULTRICESPOSUERECUBILIACURAEUTLOBORTISACCUMSANRISUSNONCONDIMENTUMTELLUSIACULISINMAECENASVIVERRAINURNAATSAGITTISAENEANFEUGIATUTFELISQUISALIQUETORCIVARIUSNATOQUEPENATIBUSETMAGNISDISPARTURIENTMONTESNASCETURRIDICULUSMUSETIAMSITAMETLACINIAEROSNULLAUTJUSTOSAPIENVESTIBULUMPHARETRAMETUSSITAMETDIAMSOLLICITUDINEGETINTERDUMLIBEROFACILISISDUISDICTUMANTEEGETTELLUSORNAREPRETIUMCRASVITAETORTORNONANTELUCTUSGRAVIDAPRETIUMETTORTORPHASELLUSCONVALLISLEOEUEGESTASORNAREMAECENASFINIBUSCONSEQUATURNAEGETALIQUAMSEMMAXIMUSPELLENTESQUEINIDMAURISLOREMDONECSEMPERLACUSACSODALESTINCIDUNTRISUSIPSUMGRAVIDALACUSNECELEIFENDMASSAERATFERMENTUMAUGUEMORBIATURPISDUICRASAUCTORNISISEDEXPOSUEREACPULVINARANTELAOREETPRAESENTSAGITTISERATIDLECTUSACCUMSANMOLESTIENULLAMAURISIPSUMPOSUEREEUPELLENTESQUEACULLAMCORPERPOSUERESAPIENPRAESENTCOMMODONISIAFACILISISSUSCIPITNISLORCIELEMENTUMNIBHETVARIUSNISLURNAIDLIGULANULLAFACILISIINTERDUMETMALESUADAFAMESACANTEIPSUMPRIMISINFAUCIBUSINTEGERNONALIQUAMESTSEDPORTATURPISQUAMEUTRISTIQUETELLUSULTRICESVENENATISDUISMOLESTIEVULPUTATEFELISVESTIBULUMLIGULAEROSPULVINARQUISNISIETVEHICULAIMPERDIETERATUTVARIUSPURUSEGETAUCTORTRISTIQUEFUSCEINMALESUADANUNCAENEANPORTTITORFELISLECTUSASEMPERTURPISMAXIMUSSEDMAECENASQUISMETUSORNAREVIVERRANISIVEHICULAEFFICITUREXPROINNECLIBEROSAPIENDUISPELLENTESQUEJUSTOSEDSODALESCONGUENULLAODIOFRINGILLAQUAMNONDICTUMORCIMASSAALIQUETARCUCURABITURVIVERRAESTNECCONSECTETURORNAREDOLORTURPISDICTUMFELISVELLOBORTISMAURISTORTORATPURUSNULLAPOSUERESITAMETNEQUEVELSEMPERDONECELEMENTUMMIUTDICTUMULTRICESIPSUMERATMOLLISEROSACACCUMSANELITTELLUSLUCTUSURNAPELLENTESQUETORTORANTEFACILISISNONLOREMINRUTRUMPORTAEXPELLENTESQUEHABITANTMORBITRISTIQUESENECTUSETNETUSETMALESUADAFAMESACTURPISEGESTASMORBIPELLENTESQUEMATTISQUAMNECALIQUETDUIMOLESTIESEDNAMETULLAMCORPERLEOMAURISDICTUMNULLAATBIBENDUMGRAVIDAENIMNUNCELEIFENDNEQUEINDAPIBUSELITNISIQUISQUAMSUSPENDISSERUTRUMMALESUADATELLUSNONULTRICESETIAMEUELITPURUSPRAESENTEGETPHARETRANULLASEDLUCTUSIMPERDIETARCUETVIVERRALOREMULTRICIESNONMORBIORCIMASSATEMPUSIMPERDIETNISLEGETTEMPORDAPIBUSVELITCRASDIAMFELISULTRICESNECSEMAEGESTASPOSUEREDOLORSUSPENDISSEPOSUERENIBHATEFFICITURMALESUADAMORBIVELRISUSSEDARCUVIVERRAPORTANULLAIDEFFICITURLECTUSIDFRINGILLALIGULASEDIACULISARCUETHENDRERITPELLENTESQUEORCIVARIUSNATOQUEPENATIBUSETMAGNISDISPARTURIENTMONTESNASCETURRIDICULUSMUSDONECFEUGIATMAXIMUSTURPISVELVENENATISLIBERONUNCIDPULVINARRISUSINSAGITTISLIGULAVESTIBULUMCONSEQUATMASSANECTORTORGRAVIDACONDIMENTUMSEDVELNIBHQUISRISUSULLAMCORPERCONSECTETURDUISETTEMPUSTORTORNECSODALESESTPELLENTESQUEEULOREMFEUGIATELEIFENDTORTORACSUSCIPITMAGNACRASLEOMAURISGRAVIDAUTELITASAGITTISVIVERRAEROSMAECENASTINCIDUNTDUIQUAMUTULTRICESLIGULALACINIAIDQUISQUESEMPERPLACERATFERMENTUMVESTIBULUMNONCURSUSTORTORNONTRISTIQUEMETUSMORBILACINIALOREMUTERATSODALESVOLUTPATNAMERATCURAE".upper():
        print(EM3.get_key(reflector=True))
        r += EM3.encode(i)
        # print(o, EM3.get_key())
        o += 1



    a = """yjxcx zvtkh ymhbs fwbeb pzhqp jyjnj fbpqu xvyfn opzau flkst npqxz vhxlz ljwsv tvkgx fbtex mguhp bqkjr wsfvm wfdcc thfxy lgaba xazfq dquho gzqes cbdjs tcmrs hyxdr mvzks gbfdo yxqsa sudwc vxele eapxe ratqu jxard ewzsi sxxwa clhkf htyly chqdx ianqo rtgob aqvms nkzjx mmogj gdshq dwkti zrizx nlygm svxoz pztjg hqptg piqid jmvud lpuin tsoth flgkr hajfd rcrfr vynaa dkyou tqrjk agupt flnlg ljfgp kgjad xkjzz qabdr ldkxk rtvlr jtzsd wxrvf gfcta hapvd wzisr vhvea weuvv fodjv eoeqb xxzjm djsxj qwdjh lefck yroft eieuh kmcrz gbfun fgjpo mknfd iqjce ikecr ijxzs jcjya uospf rynmu ofrpr lgywc akjtx fvaxu rldue taiqp huyth ftylo joavx sozqt fxhkl rwzmm lukib ukjkm egwsh klhlc qosbs xjxao mwybr bliwz dnzuq xvqyf gclqw lnrfm jfojd gtxye ubhax jcnox afvdx sznlg zsaam puyie gjrin jdbmx glbgk wnrym sauqc iwoqh btnox wjxwa jdfbj wwhta nxhhd ytjop xyqkl knyjc loojx dnfsn knigz sxgra msmxd irtvz gahtl wpkcc bjlzz mqumi zldnm cqayv jvfxq uztnw brctq inenx rasbd lonmk pbwzl yggjw zqagt dalxk klscy gwcyu dcics vgykz nzujf hrvnp fvlhv dbvwy gjjkm jjold jeblp huweo ogizl jbywk oqszu pthug wdiot yaowx zqrgw vfqxt zqeqq srghm polbn pwjqj qjxsu sxmdh tmdjr zhnto lsswl ujvev zasjt dtdlk qeufr hxrhs jvefu qrcdw iecmz ibomh oxerj efrre hupzt oclnn ijulw unhhk irpid bahft apbao iaizc thgqp tdzxp tkqez ufipk wzreb psqvm szgco wwuzc pmkms mkbph hmhmf xfuza tayax uytme emwby nnpis qzxay luubr pcrzs gfeau qefdw vqkgw iohfi rbqka vgwiq hpyes aipzg isjhe rrsmp fhald sudyz nzrkt lihua ikkba ytxxv gusya emeer xklcx wzhoa nbixs rszlm udqnw zijml xccdn lnqzk wtkwe lkqwz duxkh tyrpc xcoof zovpi qujyc jqwyi reyrs kpick hgljy cacss lrhhy nowax ddjha rgydi axoqb aaocq ccoyu egqfr pwgoq icpdh wbagb cjoki dretx sfzqi rsxdp dwzxh pzvrk ezudu nxpvj qxxml vlsnz ycsjk kmwzq izgfp ubqdh wwtni wthwd balzw opuep vwcok zxiuu ovnzp uzebj bdkcf mgnyh dycly utmtq plnnz aujnv ztfco bufay fhtbq hymzz jumeq jyrjh rvpom emnup njipx nxqlo jirai gjnsw nazwe qetlt wbitr ekiox ffexb idytl azvpc hqykh ycnod qrnsd nkzfl jdceb vvxko gakyu vyqra hvope zvmcg kuryi jfrfh vvqko qeprb iefbb aocqu cjupg ywvzx ubrut zpxfo qbrdh xcmyc uxanr fsfqf bcumd hvrkh scmlu grwyd jhkex chpki khxdt zhuyy brfkm egwbb qhxta dnyhv ypwzk prahj nbeqi pjxrd rdrxq vlaim lsbnz ftnyu eacef ppqgh sahwm utoco viach hsdpi cvanj vpuei xfzkm ehokx knzhu bqega lnjhy jiomy rcixw acksv ldaot hrztv zuzbj nfumb xkqzf xhcix qalns xqbfb ntihy jvayh jiquu bmaic uqmxc olisu kbbzz spaus rifhr ofvnh qnqdz xfjar erfnk xikdv vwsjp fnkrv kwbzn olntp yrlgz xffol wxnqe wpmez hlzqw ygoup evdkx olntv nhwtm eogrr texpf awowq gyvwe vglqd mffvu xwhom wrbwu uqczc efihd aymvp oqpry cvlra eqxft ezftz qipok xmrtl gnmaz xgavl gmnkm pxheb mpswy dvebt jukll izmko cyzsg fylyk leowo qkfww khhxl jwqeo lzwxi ipios eslvx zjzrl ikcll xsugv mnerd klahn viaxv pwxkf busce dowdo bumvb yiuhs rixiq bvsnk fpzrw yczbf iviqa bvnia qkjzz kxeix yxmmq cmdlk nprxt rtqzd thdrx cspvw ktlnb tszfm fhahi hbmhr zmpde zpefe xgzom kknqt zrzlh abnak ihcxi mkcen sayly mdgof pekqz bkaos fpkwp gsrgh ocepj zfuse dmnuc yqckf uzypf qsjcn ghocw npboh kcllm akeag ierlo eskow actrk cpfmi pubnq nqgtn eazur qpuzx uxrkn xvakv exopp uyrsh rfyyl ftsjw udaji lnvxu sgzzu ejuoq rhvxa vzqkc fwbne mpgsm svsbr tnuda kozno tnplb abbip sqrhe rysgj pqbfv zgsoh iqzfd zpjss tjckp dsymc capsg ribws rfbkg jnuop jfzzf knrum fvlvk pvtzq hwynp pqhez dmful vvtda eddri prqic zllze lqwyn qdnkp tbdae kovzx ndmur zswly ickgy ntocr iewkm exdbo hfwgp avdbt bqcje qhcdo atyzg rwuvp ptdhl joqow fsadd rziat qwkrw kqpwm jljij ievou fioqg mvmrj pcdud llmal fjaff ihrnp xvvfn inabz ydyoz umyvv nwtwb udchd hdnup nwxxh vadem lwgun ebktm ufhnz jzxhu jalfu lnqwk ytyyr hvdrq kwvkk imcny cyneo ulbtx ybhxb hotgn dyplt qvefl djlnb pokzq hlhhn apsid wnspc rqldx suagr oiocf pyude qeoxp tdvlp dacaf lrxnh vwzem hnkce sqjde kkaxr zhcwv yrvkc yxskf yzeju txtci ghlsr yqhqe mbjjr wjyxt ghjfx sjzfv oivjx jxfhk qijwv vwblb vqmiw mbzqh yjhau nwnnk idpmm mmwcw nagox neimg vbvky hkhyd aeeet ojhnu chttc thvxn wkicy weoju hbarj qstdy mhnlw jjagp vrhzo kbemk oojjy xjgdf lnjfg ikfay bckif deorr atery sohou juztk hvkui kyunc kgcmb qbmnk pqvbq zroqk uaoar imljg tzhun uzdmx rclec idevb apaeh mjskt lxyyu mbspm tdhru tttla qivsl fapzt dbjtf kcwgi ppvln vfshk xjgxt ofoxe djnkz evkud jgmix mwrhz dfqbc ocjja dovrp lnovg atzre hqhoy rrwlr hqsng yfnbq akndv ajwbx bmpgs wydon jzkgz kyqhi qlnfj muuxu kbqpd tfdgb olirq sphhf aojhr wbdvh svaeq nfyvc piisl byqja bzeva lvhnj esexi cqjxk kinhk iagkw tdwbm kszgj dmurr xiljw wfoih wfgpl oevcq jjoln ceawb hkzxv bvjbw plvfj ycflr krolv zxjnb wohbh tjkqx bcnhm pozsw vlkwx uazzu csbdb gojgl rcgjz qmgjy uzcpf lkxip skwob wwvcs ocwsi evqsj bwkxv idajx nnzav qtmjk ozdan oxsqx duqzl nnazm nxvpa tmepq mxbuq jsexe ibfmj yccuq kcaeq frgml rlafe kmiws uexkk fqyzt luxww mggli ujptv ymiea juzwl jjyps vdlny vmtsb qpspq jwzwn uoviy wzdmz ddluw stowz ndxyx lpood axahc pbchk aruje tnmna ffeqz clclc ejcgr fwaiz vrdxs sibqa xltki lhycy nuwtm magbp uhdzd yxmnw nzvgy sajds aigim pflvt wxfqh ivsgx botvj rwvvx hsmci ghiwh xwmsr kswed ccymk frexm ftqjt voxng tgowr vpoou xkgow wyewv igvfs fgvkl ltkky hzupy udjoq stijs rffhy hnhed nisdr trefu oiygh kgttk jnash jthdo yrsws ufozy oinmm tajoh ejvdv ickiz fbyzb iaahb myjjj mynqj inbcx wxszk lzbep iqseg vkjui ndnug bogiw jhclb fmxms wwixz euyij rpzez gmoea zdswx hhtxm skqox mbbpd nywsn qrgja ictmz hrtnq bocyz weifa nhbso rnxfw qhtvn xydup osykc akdwz dzmyo wxhjk bensl kvhnd zwkhs fbqew vcggd wkcet srfaj lkjbk exrxq nswep geyfa lzksg vcpod vqzvo fopzd wduwv fgspf dtblx wpber yizyy qjain mvrxy qssoj hguzi ldppy xgbwg qtcow lxyte ajvaf yewbn efsew ipbjg fehwf zkryn prznm aficb sgflv kykcq tfkvh mbovu egewd snuex pxlip nintj vpchd fnnfb ezego lsfjy imphs tzzbf oqipf sogoz yygmq gmxkn botum scsss uqbca lgpkk exiiu ucbar lhtdi jcahs lybww ckmgd xvpts fkkeq iuanx clzjo losds gfcnv afavf ogqoo weqnx bzkqa owcas ryqwb tevtw njfkn sopys rchsf rbhui flzai llthl ilkhl tugdk qkpin tjdwh syqee gaqhi cuwkm ntgef epcry vhdis dtobu ueuld qtwcq oksrf ckcvo njrec fycye akmnk tnmju jmgcb fqpqz vtety jgyox hrewp qfozm vxbpa inoeb adbcz xvcxi xursz zhebx lbtbf pspwu vlksm dhajz gffyi lmiwl xzjxd rkbkc qiiam gecza ycefd kfaag wadxl nvfof hyauo xpruj wnprb elxqp kzwob yyspg tdmsx qxjxv nngah miqyf drdsk mxuol mjalr jklau nmzme mtqpv hxekm wqdja houzg aqhff scgks jpjzg krgmg zgxob tmgcv uwabw ncrjv erubq dxwxj cjbtv isekn csrgt igtru pkncx lfmzv wvvtz xqueq qyydl swjzz xirla poikc tjmqf pxumo hwgyb rbmtr lejzd oaffj yrdid iwqno fcvxd fgtfz ckyri wtzdp wvxsa lgzjl owjpl dgqac jxoek jwpjt pvcnr jrxkx qdtbl wujwt fblmn xvjid jagvl sxmtr favbq fcfzs wkodg nulpu efvzp phrdp gfffq flkli wyxow ztpsr acsbd ocsab bnlfx gdxyf dhwzy toujw bknnb laaiq wyhui tiopd yxgkv plnod bobgl npxby hcwih jzgxn fzyma igvnk gwptb vnsug tmfkh emjts oibzr wrown vakgf lunhm cjhcu vvtcs jbstv izrew ngutc wqroz roaqh jbrtf xcrxz sxygc ulevj kzvbi zebuc yjjcn xgkzz exzzh mkiwn qtwua bbqqf cdwll atyjl cqtpr rdaij olqxf cokdc kllbk enhiy cnmob enjln mavcw tsqrd lhacu abbji sjokr sixwb pbwzl oogrb leanp wiyso pdkwr essae lwzga yztdd hkqay cifmz ooqwm odmmv aziiy vfneu gjlae eofkp hpvdt ukqlw rxcpl okdgo vqabd kelpg aoupm vaazk ueqgl osdul hgvdh sqcek mjppo vualc kwfuj ikale jrkzc nbqdi ghupg orxlp ldnur moejg eoafl yoozr hkocq xbvms elzqt ibuqy ylsch cvgmg pfeqt vkdwz ikjzw wnvqu wkgds ogqjd absip diluh xoroa xddys ellnz lyfyq hkkrx fbxfa irhme pioiz jbqdr kdhms mgcvr oqizc lkboj zvszh gpcsh zeumf pvdrx pzbrj ykdxj uwsvf ewbkj hbtxw nazez ihjmi utrki dgpnz nnmhi osmbj dguyb wanum knbjz crafw xnmud yycvw hahbo hvolr pgyld hqtis mwhaz matik ciwgj ykipf oszvl dwudc tfiiy fbqpm lwprx ugcfj vflkg gsctq jbclm syqpb mvqzn gpkmx ulxtf zjazr jsjzg mjupg uzvdw mjpqa asobo uqhto smobn yvkcd tdpvq keuvd dcqwl rnnvv kshkk sbzfi shyll htyar vpaow ppbkk tjuli xxtmm ahxof ljoog zxmww yixrr woziv dsnja avwok vscgf vzbui cyyvh beyiz jqhki lamqu hnnrt neqhn chqzd ozpip cttqk yswnq cnmqb wunla gkdzq mweke eugnx landp repgz qtdbm xaiag uwcxz cypop lklse sfsix qjnqf kgtpy afvqp unmvr yaqlv racfj cuxfc hlcbn qhmqa bvukw fjuki xdwzf beszb hzkcy hafxs muqco jivon woatn ktwtp lktyp tzpgl kfaue qkixg txfhi bqggd kiaoo akweq uhdzl xzyum dwndq felug bjavc gljys qgxke lnihm zehka xhmii wnaju psydq ogcgt yqums efloa krtod nbdex pwhew jtczx stoph gqorp ujuhs vyoda fjfqd qxvzu lvjkn dyemk avqvb txgwk mkdcl yphkb szdzk msprp tghey lvsxc qmtnf vgpic ywcel xzjpl lcvcj yhkog yfpiv fnyww cpfrb tyrhv aloar uhqui yxufr supho dwkvm hlimd rutbh qkbmu ddiir pvbub blprl aqtra kzozh gzstb lozop htgsn shlis fcksp itjsl livtz ellrw nxyim ewzab lboez ntnsq tglip lhhak kicmj sjzbr bysax lvmxt hpble wysuk sssxz xlrkr sjbwx rztpd zvkob xlftz ghuna xwmfx alcvz kbawf aupyz gncvf eohqv rggyo nyzgi bkscs gstbb pmunv mzcwg rtajf szbyy azreo tvdjf zlaiw daybd atbxb npgty qjpxt jrfnc igpzc galpe atgih koqtl zsdjj faged pfyhu rxidv wbiwz ytcvg ugamq whfnz tpmff dqbkg kmumw dvmnb kduhp xqlgt bbgtk dnxrp zfsfq zwnsp xqyom nqgbd myjis ziwgd jxsfd uvzot kendq zbcpn fznme kgelx decxd ygigk pirgx xnwvy cdomg slzkh sxxoz iyrhg sqmup gvwpp lrmlg flnie kljgl xvupo rovts apxgx jubla tmuqa qotlq clwrg rrbhb ewntg puwkb erpve ujnaq yycpd bnyvi eqfqa xvgjj focba bpkxn ksttv wykux bzmof bvlck adyrm gcxbm bczrz ayrrp rnsrz mxvpu rkdmq odesu tyyhl jdpts onflh iimgp kofco dnslu ubghy oasxz bvcxj lthgq pxaeg plgyi rqcgm bwuat ndbym vahbx xfftu elrdf nxecd hltdu ibled dlyrw eqipx migii pfglb zdxnu iffoq cvnzq nuzaw aejsp rnpow zihle cjxnl fjyof maiwo zbkbw souub onxqv axctg zgiej skaky sxcrv yhniu itwrv nqgvj qjeof mmmac yewvt bfial tvsbm trmgj hfqgy vkvtl ijpox cdmcc ggqra xjwde zcjfy jtdcz gzmqm ohote itmxn ossoj hblji zddwk ehkiw ynvuf ejkeb fsruv zmlmh hgngs agikg hpuue cwsce inzqp hxmky trxno zycrb ezcaz juksi kpjbq ixdlh yxarg kevwd guskk wdszl hfyks mnpqr zlnjk pzmbi fmdsx iklbw altrr xsaoz jepav nkidq wrzxb zsvtt abcqm mcaan egurv ghdxc dghex tqxuq wxjfu vdgwm pfpjo poagh vuprr cglxp udsga thjzc kbdnz uybsv mhjql vvebd xurte xdzcx zzdla ijvai oswry neqnm kjono cnlaf ozgkk guxtb ybtiw idvvx ddqdi rumms yifob orlqq gaqwc snimt qjvvr lhhui klihh dzici aprbw gcgcc pgcdd oltll glswa rejgj kpuyp ewqgs yhyhv gufzq cxzca yukym wmjqf wjchb xilyf wljwh apveo icclx ttyft zzuba gwcsq xdcst ymcjt fqsyd zxwmd hqpib lqobn krayu pnccq meuri ynpvr reybd gtwzu kespt zzhpv wgvyf kbgwt vteiq ptswy psegb gsujz ffkjy yhqwf gatll vpccn obezy jdicb ladej rrdnr bihsp ksmas zmqoa hgitm wyqse aaxkt xldxd kxkij ahadu hcsmf ggche phdhs qjxwo pvxwf simvd arelb ksxll nwrja dkjmv ujifm bslwc yqljv bczbn cevvt ztzhr mwuzr fjqsa gezfj ngnlu czznz gkkvd ayuzj ghhui uycbz rapts rtwae kjeay dpvhs ngnto bqslt cnkvp ygkwz aydnd lnbrw onhlc thusm lxsoe bazuf ebnui yarzf kczmc jbtdz btfzh bxhji gabwi rwsdb fnmty pisax upuwh rddso ewgfj rupja epgkz ztfpd tzzji kfelk muvkc wanij apbeb dhvpj rfckb djyni zleby sygjc kaaok mfzvj yrplk vgkpx ltdim icoyy fdgjl fszqh mpuar cgvkl zqqdf zqnrk qdflj cwume cvrfy bywsu nlnqd wgyyv fqbfp sheup tggjx iervs oaxce lgdwn nodut czyoy pjcji aoydo ltyod ugpca spqwx hjlgn qourx vmoax flank ictrf djxcz ugkdo jnvvb xfhly kfued oyxqp lgout qlqls iqjfp nljzh cmlvb ezpky rlcxt sqiya gfoha kicoq uzhrg mmdix psmtn sqrwt jzikh yzqmc jruda siujn kicqq eivol cvhgy zekfi jqies mxdsg dgxjn ccwxv jjqpo vxzio vfvcv rsbjj sboak orjrb bcqpo bubef bpxcj otaoo njyzg aszkl ufndt rvcwx dnftl ugtle qevam qwkqa rglbw nfbdo hcaze dtviv xwmdp leirm rsmjh ovhdo ppbow kddby mckwd tpwcs okaot abczw hdxjp yxwlq jppqp pbmrw pdspu ztdtp uhzki prmie gwhhx hdtyd szqiw bqgzh udrzx wglhe uysyj sdtni hjefj cyuxt bdbbm ikpdc sfdte alaqk ontuz nyvzi sobpi cuufu syjtn ijlkv yirrc kxclc mstrb mtaob xotdf gyqrw ufniu igvvp qwodu egbfu iuivi njrif nxuef smqmm oxjdg jkwdq nbqii zvcvj ufhpd voylo jjvpx cduho qrxwg rndcd fqrfd irptz qgfjz oodvd sdfyf bevhd xuluc fawed crhco xnzjk vtlri djtmh kaatj zitsc zukil mruna vzvky wmmuf xqtdn yoshl wwtga ltmsg jruii tnycm phobu bhjao lbtag dckxw msicx vlqrg qttss rhdoz cuupa akvff jlisk sstgj guszw gnvlp thzhy jdxwd byocl evkna oearp wscqg ntuvw ydmid buqth wyrha utwec lfrop pzqyy flxqx dhpfs nosib ynxfn qccks npqrn whwjs nxrmg iixzc ibxbr jqwze rjqmf kgjjb bjlyv segvk albod pyera unceg vatgk tbyns dthwi lnyta gccht gmpzq tmfvc ubodp uszll czbuc szkux ddxrm fycss ogfkt fsbrc hvprk iwhst oqjkp aohrn yadzh qhcjf cijfb dpubb fyfcz fllry afekl gqyxz ayycb avqqt bxjzj sanzh labcd xcyet eesqj kyqeh bkbja iolje ghoyn omsqi mklbj dnivb hmrmf tpgmn fszvm ojiml iytcx xxous ytezy iuxjl phjbr fwotu knygp xekwm mnfaa leyau ghcun hejve njwrk gnfpb qviod bkaol avqza iztsa helpt exfkh nhhyk lcwrv gjmfo bkhrj mkgyp auwsd syuqk puupw ohhha zckcj xxerh xdcer lfiva lohhq cxaie dhpfu cakpk eycoa fdmgu apwzl rohuv hzema igstt zhpmu vbkzq cbazq eoost svyeo lfjdt locry mgycx zniks nreeq mkxbn qpusb wcesd favlu cidyo efxfp eydfu dcext dhorl blbew irmrd wdchi yzpnr fxaer ghzpj mfvve wujkz rjpfx fyqkv gkqah oayoj pkpgb npmwo pqbld wxivr tayvu qnuuk uuvgj bmyqi uimve iwghu bdzcg bqzuy uejsm sfrnu lqdzr cvscm efebt uevnv cjsih afsfg sxwrn mllqf ctpcx lsgzp mzvog ajupn tapak propr ccrby ufcji gzmkq hilyn kztcq uwswg zgqhb qiicg fsxul yuukf dozfe doggn jxqsg hoyoe pqhtz muozr asjto qhaoh uptlh zftsb fkweq vilkq dlymx ccfqc furng avtcz zzadd qyjni ihoml vfelf aihpg xnaol erlsc cwwjr ofivo qqmdf jhwnt jqehv ofmwl obcpz phxdo yradx fyjnm buutn wryvl iardk xdrbl ourhk mxitw ssxgu uiiqm hdvsh rozkk hjfcc cgacd snyre kbapj gnpgx suecy kmgml mbags xbsba jgydx phrog yiejt bgcam stkrw jnxmv jdtvl fpvfk wdoev uvpox ubtbr afylz ewdtg ltkpd dquhf ftits zxqma cfaei vcphz kjpbf hgmef rvcyx ivnqi lkrsx uoyfd uugog dyiml iikxn xqxwo sgbtv bdzgf nmlhj akfkh xlvow voatb cvsju chjrr bkpns xqlso ryeqb pzpzl ywsqo ymsyw hlnbi etwsz pnfpn iyqps vnhcr exxbq qqzwm mbqll psndj ryfys dutoi ijklb utvfy nmynz vlshd hxbpf heywo yvkdd jsgon myrle mrwju minbe rlbez woxcm oukum ygwzk dnckp xqcdi qgqoz uglyd zmjgy fwkfy vghis pjhmf yrddt fsesv brzhp qbhjk tpogy dsjlj wmggc smmxm ubqdi mqzku kfmiz lyukz wrqtf ctwfh ohjqq txbum mmqyw zekih roevn ahcns tgyox qrbrg yzgan xjvxb twotd edpwe tkymr uxmbz lbucz nuxld mreos rizls wjoto cilho ttzzn ofpkp clhui kzfvb ptarm sinvq xzqfs cckqb kwafx utcyg tevok rqmnf obrbu wfysw imzdw nbxdg vfuzj efkbc shlnc qrapw jbybr ceyty wnjfj atffv eckez mubzb rkccq ltvdx hvfwr ujdpp skqvm xmqkj oimtq aovdv xmdrp deyob dxary lclkb qextr uudjw ojjfn hiiew pdlwz trczb bekak cxogg ebnhk mdqal vqqfg crzsu cpwib zdkmd rchan kyaiq egcxv cfucz ofbgn tdxuz tehbb vvfol siiif fdvxz qtras rjgfu shmab iorgz vmvso jcqnn vfgxk kvqpk wgofe studz muiny fdbzs dnipu ofgzb feclr ccrsp iycbo omrom kcnck rwqyl dxzuw xldzf njyyq zrtfa hozou tyrvy jgfan xeyai xfhlw kwaxo hntri ljbry ndlit jdjds wgylp uovls kdugm tgwgz vpcvl goedu klxfz tpojc yyyas asvjq ssmrx hasrv tgknf lsfvr phgyk zzkzh uwuuy qfojy bmlpr poixr nytoc grnqu dknfy dgbwo orxmt kncyk axsms bopql fonci qplmx jjeiy vwrps wyrza bwcid rzzok ongup rwxqk hxtiv mzoiy iluga ucxjy vdzhz mtwyv njvyf txict fcxke dpolw ksfwo kdqlm jfiwg pwcjp brpkf amepj bpxtv hhuyc cmery akder oeyrf omzoj miixy mxgod knxja uzytb uzivh qshjn slqct avejc shwal eafpm fixkk hihci szvin vacmz ydnnm yoqff rzdnu ipfan colwt mbvjc jyimn iupbl onyxr akfct swwjq jlkpt aeddz vflaa pigmy ugvhi rsoyi hbcrp lbvzp alpgm mlhvs pvvke wodhq qiquz kftsm gjeli jpuok naovh sgqsz qkyfe svzst uzvqu wsviq gwfbr usvee ilrdd joosb ildto wgjut yuozc qclrj nkssd dylfc kmoez ufkop bkean fopmj oilwg wuikv ifwrb wkukr piryl ingwk jtjph dpjtq rgyep yckpl darly saida pdtfh ckusj nbpvw ibozn dkxpj xijkj qaufr yqliw aycae bdiwq fplsx bjhvy eqbgu vluyk cqvjw jxxbz lcvxm yzxos cdcjv qfbjw bwneu kyfbz ovyru cgeyr ijlns cboef kdlxd huqpk ijgsg tyhao myrcr zucty bduar odjsd thlcj idvik fnjwy qgdma ihcsv hvdyk udlvx hdrea jzyuf tkwpd usrlk akmkr noxpd eqdtq lbjme ewvak psssn ybymo fqagn pccas hsmgp fukyh rnfzh ndfik txfgz bcwkk bluhv lgkjd pcupx rrmzv qflwp pzvmg oguks pzswz wzqxj uojpk opwjm wqwdg yceue yzvyc pmukb rambb clvej lrebn pjivv tngsz nqoxs eljqy ofcjf grvvb borah amozh hnevw ztcya ubjry dwkfh dfgjo jhnfl slrbp iikdr cnpgm dwbxd wcpgk ybkdh gftmf odlii uzjab hbazb yaolh mqkff vylbc ffwey rdkas ckvya dlqow gyrah yklqf fjwdq kezbf ljzhz vywrm cqokr etxkl maejq riyed hqibf trnyp ozfku qsquh vuqgm aogut qoqlf qxdah hquhh rptpv ykncy tanoe xxatc jkluu gejzv qqfjp axyvs iwrjj vufok afdsr twhve mdbny clzyv fgjvf bnhqh luqeo ykqfm luiog wqgba pardc tuuzp grqbh lrhcd ubgye etjuq ewood qepzk gkaef iuebc ewsur pqmud vhlyn nvjiq gpxza huhgg kxcgp yfrom yadxn nyjaf wnyqu bvtcs ubuyy mbynk wcscm rshfk jfrll vqamv zpdyp vigyh jraji ddiym nhrmm rwqwb mpeft qhhhs medve yczes nmfdg zvrmm vknjj tnxll xdcbo yltnq kdovo vkxvi aitds kjarn lxdmo kpchh wxiro wvsdl pnsiz tihqr svlqz ulfww aezyt uptbs wesrv fmetx ilelz jmntn dhrtx jmxkj rgnob nnakb ounwb racfy ubyap rlfsk hsjyd eaeyb vgnsx ggxsu stpoj tcnpn zommb umfmg tiibh qzwex rcdkx bwpsw jkvej yraqq nvq"""
    a = a.replace(" ", "").upper()
    for i in range(0, len(r)):
        if r[i] != a[i]:
            print(i)
            break
    print("================")
    print(r)
    print(a == r)
    print(a)
    print("================")
    '''EM3.set_key("PDN")
    for i in range(0, 20):
        EM3.turn()
        print(EM3.get_key())'''

    temp = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent et eros vel neque suscipit hendrerit. Maecenas lorem felis, viverra a tellus sed, scelerisque laoreet ligula. Suspendisse mi nisi, vehicula a vehicula porta, tempus eu quam. Nulla ut pulvinar ipsum. Cras nec consectetur leo. Morbi aliquam et velit ut congue. Proin ut ipsum leo. Nunc rhoncus, orci ut pellentesque malesuada, leo enim volutpat ex, nec pretium nisi diam tempus lorem.
    
    Pellentesque quis bibendum magna. Aenean ante lorem, auctor at pulvinar in, viverra a tellus. Pellentesque erat magna, fermentum quis ligula vitae, sollicitudin dignissim tellus. Donec sit amet sem vitae odio egestas aliquam. Praesent ut egestas tellus. Aenean sagittis magna velit, sit amet vulputate elit aliquam eu. Quisque tempus mauris vitae dui placerat, a tempus ex euismod. Quisque a felis id ex facilisis egestas a sit amet mi. Aenean in convallis nisi, nec porta urna. Maecenas eget nisl ut lorem condimentum pretium. Sed placerat, nunc ac efficitur hendrerit, nisi erat consequat elit, tincidunt sagittis diam dolor sed lacus. Nam magna metus, pulvinar eget risus sit amet, fermentum posuere orci. Integer placerat tincidunt orci pulvinar ullamcorper. Sed a venenatis nunc. Vestibulum nec gravida dolor, feugiat cursus neque. Sed sed porta lacus.
    
    Aliquam erat volutpat. Suspendisse aliquam ultrices lorem, nec dapibus nunc tempor at. Nunc venenatis lorem lacus, sed ullamcorper sem congue eu. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Morbi eget condimentum lacus, quis tincidunt mauris. Vivamus hendrerit nulla sit amet sapien volutpat, eu blandit turpis rutrum. Interdum et malesuada fames ac ante ipsum primis in faucibus. Proin sollicitudin risus nec facilisis convallis. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. In posuere, libero ut faucibus tempus, ex nibh imperdiet erat, laoreet pretium nunc odio facilisis magna. Nunc facilisis ex eget dolor mollis, et euismod urna tincidunt.
    
    Aliquam eleifend tortor et mauris pellentesque, non commodo lacus faucibus. Vestibulum at malesuada ante. Aliquam justo urna, placerat eu purus at, commodo pharetra orci. Mauris sed ipsum sit amet metus congue fringilla in et ex. Sed pellentesque convallis leo ut malesuada. Donec consectetur, lectus sed rutrum imperdiet, mauris est ornare justo, at consequat ligula magna vel nulla. In mauris magna, pulvinar non mauris eu, sodales vulputate nulla. Donec eu elit eros. Vestibulum luctus eros lacus, nec mattis massa dignissim nec. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Maecenas et tincidunt ante, facilisis fermentum justo. Integer malesuada tortor in ante tempor tincidunt.
    
    Aenean venenatis, tellus et luctus sagittis, dui elit maximus risus, eget posuere ex lacus et sem. Suspendisse ut pellentesque metus. In lacinia turpis lorem, nec pellentesque leo gravida vel. Sed eget ante in dui elementum interdum. Vestibulum id lorem orci. Nullam maximus ullamcorper dolor, eget efficitur massa molestie et. Nulla imperdiet aliquet odio, sed hendrerit velit facilisis sit amet. Suspendisse nec mi quis orci gravida fermentum. Vivamus vitae bibendum tellus. Sed eleifend libero non lorem maximus, ac tincidunt leo porttitor. Integer sed dui metus. Vivamus quis luctus lacus. Vivamus rhoncus tortor at tortor luctus, non tempor sapien vehicula.
    
    Nullam magna neque, euismod at sagittis ac, sollicitudin at ipsum. Sed vitae sem aliquam erat maximus consequat eu a nisi. Duis in molestie enim, eget luctus mi. Integer eu sagittis lectus. Mauris vel tortor quis dolor viverra volutpat. Duis dignissim urna quis tincidunt pellentesque. Aenean accumsan et velit eu pellentesque. Duis felis dolor, scelerisque vitae elit tincidunt, aliquam interdum sapien. Vivamus auctor vitae neque vitae sagittis. Quisque eget ipsum massa. Duis ut nibh id est tincidunt ultricies ac non velit.
    
    Maecenas at lorem dictum, fringilla magna nec, faucibus nisi. Vivamus ex nulla, semper et leo quis, vehicula vestibulum magna. Sed blandit bibendum massa non sodales. Mauris ullamcorper bibendum nulla et pharetra. Quisque ex velit, tristique eu ipsum a, convallis blandit nisi. Phasellus nulla quam, lobortis eu commodo a, vehicula ac ante. Integer ultrices facilisis porta. In vulputate molestie purus sed fringilla. Fusce ultrices dignissim nulla, non fermentum justo condimentum ac. Donec consequat turpis sed lacus porta, nec posuere elit viverra. Sed quis commodo dui. Donec lacinia velit ut augue consectetur vulputate. Pellentesque egestas ullamcorper ornare.
    
    Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer consequat, lacus ut feugiat ultrices, nulla augue feugiat metus, nec tempor nisl quam a nulla. Nunc interdum mauris sit amet justo interdum elementum. Curabitur vestibulum arcu in ullamcorper sollicitudin. Nunc pellentesque vestibulum mauris, sollicitudin dignissim tellus porttitor sit amet. Maecenas nec sollicitudin augue. Pellentesque fermentum neque tristique mi dapibus, ut iaculis dui rhoncus. In ultrices est mi, a condimentum erat maximus vel. Donec commodo sed dolor vitae lacinia. Praesent fermentum risus quis odio vestibulum, quis aliquet velit varius.
    
    Praesent malesuada tincidunt ipsum, at luctus sem volutpat porttitor. Vestibulum in vehicula velit, non vestibulum ante. Duis consequat enim purus, sollicitudin consequat velit pellentesque eu. Etiam ullamcorper consequat enim mollis accumsan. Nullam venenatis euismod sapien, a cursus velit malesuada ac. Etiam varius a massa eget placerat. Nam tristique tellus enim, ornare dapibus felis efficitur ut. Pellentesque venenatis iaculis eros ut pellentesque. Sed tellus est, ornare tempor sem ac, gravida convallis nibh. Curabitur semper, justo nec convallis interdum, turpis felis bibendum arcu, quis suscipit neque nibh id neque. Etiam auctor nunc vel vestibulum ultrices. Duis scelerisque quam id risus gravida iaculis. Pellentesque consequat lorem quam, eu porttitor erat scelerisque vel. Nullam ut ante consequat, accumsan arcu a, tincidunt arcu. Phasellus quis nisi porta, sodales velit vitae, ultricies odio. Pellentesque facilisis tempor justo et rhoncus.
    
    Proin nunc elit, gravida ut massa ultrices, fringilla sodales dolor. Nullam sollicitudin dolor lorem, ac ultricies ante dictum ac. Nullam finibus ipsum quis neque hendrerit mollis. Phasellus efficitur lacinia sapien vel egestas. Fusce sit amet auctor justo. Curabitur sem dui, molestie nec imperdiet a, auctor in mauris. Aliquam erat volutpat. Phasellus consectetur neque ligula, sed ultrices leo ornare dignissim. Praesent quis metus vel mi dignissim ultricies. Nam viverra felis nulla, eget imperdiet odio maximus quis.
    
    Quisque a aliquam mauris. Nunc nibh lorem, hendrerit faucibus leo posuere, vehicula euismod lorem. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Quisque sit amet egestas lorem, quis malesuada nulla. Donec turpis velit, ultrices vitae scelerisque eget, commodo eu mauris. Curabitur ullamcorper, diam at ultrices commodo, neque mauris vehicula ante, eget ultricies justo neque sed tellus. Donec dignissim imperdiet ullamcorper. Morbi dictum diam fringilla quam egestas consequat. Nam augue nisi, sollicitudin ut libero et, feugiat interdum augue. Phasellus at odio fringilla, rhoncus elit sed, suscipit erat. Phasellus ac mauris est. Nullam cursus nibh nec mauris placerat aliquet.
    
    Vivamus ullamcorper velit ornare, interdum dolor sit amet, vehicula lorem. Maecenas in neque ligula. Suspendisse potenti. Mauris eros libero, semper id laoreet vel, imperdiet et leo. Phasellus in fringilla odio. In vitae lacus sit amet sem tempus euismod. Suspendisse ut tincidunt eros, in luctus diam. Sed volutpat vestibulum nunc porttitor hendrerit. Etiam ut sapien ac eros ullamcorper bibendum. Nullam mattis arcu sed purus vestibulum, ac auctor massa vehicula. Morbi dictum nisl vel quam fermentum, et fermentum felis pretium. Sed vitae magna a arcu vehicula ullamcorper.
    
    Aenean magna felis, sagittis vel tellus et, sagittis varius turpis. Vestibulum posuere vehicula urna, imperdiet gravida velit porta et. Fusce molestie dapibus viverra. Cras nisl arcu, condimentum nec accumsan quis, dapibus in justo. Duis vulputate accumsan felis. Donec sit amet massa non erat efficitur lacinia et vitae lorem. Nam sed elementum orci, eu porta metus. Praesent lacus magna, ultrices vitae sem nec, commodo cursus leo. Nulla sit amet velit non nisi ornare aliquet in eget massa. Nullam aliquet quis risus vel aliquet. Curabitur eu ex metus.
    
    Quisque viverra euismod elit convallis vehicula. Ut eget lacus et mi condimentum mollis. Etiam auctor risus commodo sapien maximus, eu lacinia tortor vulputate. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Cras a magna urna. Pellentesque varius, nisi id viverra tristique, sapien arcu sagittis odio, vel pretium libero erat id mauris. Maecenas sed quam a enim condimentum dictum a non erat. Maecenas vel elementum odio. Nunc fringilla libero ac enim condimentum pharetra vel eget erat. Mauris in diam feugiat, imperdiet ligula at, auctor lorem. Proin facilisis, turpis vitae sollicitudin blandit, urna purus porta libero, quis molestie lacus arcu vel ex. Nullam vel tellus sagittis, lobortis nulla non, blandit nulla. Ut sed porttitor lacus. Vestibulum imperdiet massa felis, sit amet fermentum sem tincidunt non. Sed ut ligula purus. Etiam et lobortis enim.
    
    In blandit ultrices laoreet. In est lectus, ullamcorper sed ligula blandit, vehicula ultrices massa. Cras ultricies augue quam, in ultricies arcu scelerisque et. Interdum et malesuada fames ac ante ipsum primis in faucibus. Nam quis ex vestibulum, eleifend sapien ut, tincidunt eros. Ut egestas sem arcu, eu imperdiet erat tempor rutrum. Etiam faucibus nisl eu nibh tristique, id aliquam eros fermentum. Mauris aliquam augue eu consectetur suscipit. Duis non quam nec eros molestie laoreet. Aenean erat tellus, rutrum id ultricies a, dapibus ut felis. Phasellus hendrerit posuere eros, vel condimentum tellus dignissim sed. Curabitur elementum dui in mattis fermentum. Mauris feugiat enim ac justo aliquet interdum. Nulla eget hendrerit felis. Vivamus gravida, ex at venenatis scelerisque, ipsum augue scelerisque velit, at volutpat ligula arcu sed dui.
    
    Vivamus auctor leo nec odio vestibulum porttitor. Curabitur sagittis, nisl id accumsan elementum, turpis ligula congue nibh, vel vestibulum purus ligula porttitor metus. Donec tempor, augue vitae venenatis suscipit, tellus massa ultrices erat, at auctor lacus tortor a eros. Nam sed finibus tortor, sed dictum nulla. Fusce elementum odio felis, sed eleifend eros fringilla et. Quisque sed tempus justo. Donec vel hendrerit dui, et euismod sem. Cras volutpat eros odio, eget ornare elit hendrerit quis. In feugiat, ligula quis ullamcorper viverra, nibh nulla euismod nisl, et aliquet sem tellus a ante. Curabitur viverra felis mi, ac efficitur odio sagittis eget. Nulla aliquet, tellus sit amet tempus consequat, nisi ipsum porttitor ex, quis dignissim nibh tortor molestie mi. Vivamus at quam sit amet metus tincidunt tincidunt vitae quis lorem. Nullam metus ante, lacinia ut tempus ac, pellentesque nec felis.
    
    Proin hendrerit at mauris quis auctor. Vestibulum vestibulum diam ac tincidunt efficitur. Interdum et malesuada fames ac ante ipsum primis in faucibus. Aenean facilisis consectetur gravida. Mauris ultricies orci quis lacus ullamcorper, sit amet accumsan nunc bibendum. Nulla nulla felis, aliquam ut ultricies sed, aliquet et metus. Vivamus velit felis, commodo in velit at, eleifend viverra felis.
    
    Cras et mollis est. Sed pulvinar erat non rutrum maximus. Morbi id massa elementum, vehicula sem sodales, venenatis odio. Etiam ut hendrerit eros. Suspendisse lorem nisi, pulvinar eget orci ut, congue rutrum orci. Sed et egestas libero. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Mauris aliquet nibh mauris, in euismod arcu tristique vel. Vivamus vel finibus velit. Aliquam eget elementum magna. In hac habitasse platea dictumst.
    
    Pellentesque malesuada vestibulum tempor. Ut non sem ex. Nullam congue lacus a odio volutpat, in tempus nunc aliquam. Suspendisse pulvinar sollicitudin ligula vitae dapibus. Donec eleifend elementum nulla, ac faucibus est posuere ac. Nunc orci risus, semper non ex vitae, pharetra dignissim tortor. Sed efficitur auctor semper.
    
    Morbi quis erat a nibh blandit vulputate. Praesent varius viverra dictum. Aenean dolor lacus, vulputate et urna vitae, ultricies interdum massa. Proin ac ligula eget sem scelerisque sodales vitae ut ipsum. Pellentesque mauris sem, euismod non elementum at, hendrerit ut leo. Phasellus consectetur ornare tincidunt. Etiam elementum nisi erat, a tristique lacus tempor ac. Mauris eget consequat ante.
    
    Integer iaculis viverra ipsum. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer pulvinar vulputate ullamcorper. Sed id ligula quis magna vulputate placerat. Praesent eget tempor dui. Aliquam varius ante sed lacus cursus aliquet. Quisque at nunc efficitur eros pretium gravida nec eu enim. Vestibulum facilisis a diam vel vulputate. Suspendisse luctus quis metus et scelerisque. Nunc imperdiet aliquam tempus.
    
    Fusce ut accumsan metus, sit amet suscipit velit. Aenean accumsan risus vel ipsum molestie, nec mattis turpis tincidunt. In lobortis, quam eget ultrices rutrum, tortor dolor fermentum quam, vel euismod lacus risus et mi. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Ut lobortis accumsan risus, non condimentum tellus iaculis in. Maecenas viverra in urna at sagittis. Aenean feugiat ut felis quis aliquet. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Etiam sit amet lacinia eros. Nulla ut justo sapien. Vestibulum pharetra metus sit amet diam sollicitudin, eget interdum libero facilisis.
    
    Duis dictum ante eget tellus ornare pretium. Cras vitae tortor non ante luctus gravida pretium et tortor. Phasellus convallis leo eu egestas ornare. Maecenas finibus consequat urna, eget aliquam sem maximus pellentesque. In id mauris lorem. Donec semper, lacus ac sodales tincidunt, risus ipsum gravida lacus, nec eleifend massa erat fermentum augue. Morbi a turpis dui. Cras auctor nisi sed ex posuere, ac pulvinar ante laoreet. Praesent sagittis erat id lectus accumsan molestie. Nulla mauris ipsum, posuere eu pellentesque ac, ullamcorper posuere sapien. Praesent commodo, nisi a facilisis suscipit, nisl orci elementum nibh, et varius nisl urna id ligula. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus.
    
    Integer non aliquam est. Sed porta turpis quam, eu tristique tellus ultrices venenatis. Duis molestie vulputate felis. Vestibulum ligula eros, pulvinar quis nisi et, vehicula imperdiet erat. Ut varius purus eget auctor tristique. Fusce in malesuada nunc. Aenean porttitor felis lectus, a semper turpis maximus sed. Maecenas quis metus ornare, viverra nisi vehicula, efficitur ex.
    
    Proin nec libero sapien. Duis pellentesque, justo sed sodales congue, nulla odio fringilla quam, non dictum orci massa aliquet arcu. Curabitur viverra, est nec consectetur ornare, dolor turpis dictum felis, vel lobortis mauris tortor at purus. Nulla posuere sit amet neque vel semper. Donec elementum, mi ut dictum ultrices, ipsum erat mollis eros, ac accumsan elit tellus luctus urna. Pellentesque tortor ante, facilisis non lorem in, rutrum porta ex. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Morbi pellentesque mattis quam, nec aliquet dui molestie sed. Nam et ullamcorper leo. Mauris dictum, nulla at bibendum gravida, enim nunc eleifend neque, in dapibus elit nisi quis quam. Suspendisse rutrum malesuada tellus non ultrices. Etiam eu elit purus. Praesent eget pharetra nulla. Sed luctus imperdiet arcu, et viverra lorem ultricies non.
    
    Morbi orci massa, tempus imperdiet nisl eget, tempor dapibus velit. Cras diam felis, ultrices nec sem a, egestas posuere dolor. Suspendisse posuere nibh at efficitur malesuada. Morbi vel risus sed arcu viverra porta. Nulla id efficitur lectus, id fringilla ligula. Sed iaculis arcu et hendrerit pellentesque. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec feugiat maximus turpis, vel venenatis libero. Nunc id pulvinar risus, in sagittis ligula. Vestibulum consequat massa nec tortor gravida condimentum. Sed vel nibh quis risus ullamcorper consectetur. Duis et tempus tortor, nec sodales est. Pellentesque eu lorem feugiat, eleifend tortor ac, suscipit magna.
    
    Cras leo mauris, gravida ut elit a, sagittis viverra eros. Maecenas tincidunt dui quam, ut ultrices ligula lacinia id. Quisque semper placerat fermentum. Vestibulum non cursus tortor, non tristique metus. Morbi lacinia lorem ut erat sodales volutpat. Nam erat curae. 
        
    """
    temp = temp.replace(".", "").replace(",", "").replace(";", "").replace(" ", "").upper()
    temp = temp.replace("\n", "")
    print(temp)