__author__ = "Marchal Florent"
__copyright__ = "Copyright 2023, Marchal Florent"
__credits__ = ["Marchal Florent", ]
__license__ = "CC BY-NC-SA"
__version__ = "0.1.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "Development"

import Rotor
import Errors


class Reflector(Rotor.Rotor):
    """A Modified Rotor that assure that if the result of forward_reading(value) give value2 then
    backward_reading(value2) will gave value."""

    @staticmethod
    def _wire_inspection(wire: list[int] or tuple[int] or dict[int]) -> dict[int:int]:
        """Internal Function. Return a wire that can be used by a Rotor.
        A wire is a dict that respect the following rules:
            A: All keys are integer between 0 and dictionary's length.
            B: All values are also keys
            C: All keys are also values
            D: All keys / items couples have to also be items / keys couples.
        :return dict: A functional dictionary"""
        super()._wire_inspection(wire)
        for key, items in wire:
            if wire[items] != key:
                raise Errors.AsymmetricWire("Reflectors' wire should have symmetric key / item couples."
                                            f"'{key}'→'{items}' then '{items}' should gave '{key}'")
        return wire

    @property
    def rotation(self) -> str:
        """How this rotor can turn
        :return str:  'normal' or 'reversed' or 'without'.
            - 'normal' - This rotor turn in the normal way : Position increase at each <self.turn()>
            - 'reversed' - This rotor turn in the opposite way : Position decrease at each <self.turn()>
            - 'without' - This rotor do not turn but next rotor can turn if previous rotor turn."""
        return super().rotation

    @rotation.setter
    def rotation(self, value):
        """
        Modify how this Rotor can turn.
        'normal' or 'reversed' or 'without' or None.
            - 'normal'- This rotor turn in the normal way : Position increase at each <self.turn()>
            - 'reversed' - This rotor turn in the opposite way : Position decrease at each <self.turn()>
            - 'without' or None - This rotor do not turn but next rotor can turn if previous rotor turn.
        """
        if value is None:
            value = "without"

        if not isinstance(value, str) or value.lower() not in ('normal', 'reversed', 'without'):
            raise ValueError(f"expect 'normal', 'reversed' or 'without'. got : {value}")

        self._rotation = value.lower()
