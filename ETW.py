__author__ = "Marchal Florent"
__copyright__ = "Copyright 2023, Marchal Florent"
__credits__ = ["Marchal Florent", ]
__license__ = "CC BY-NC-SA"
__version__ = "0.1.0"
__maintainer__ = "Marchal Florent"
__email__ = "florent.marchal@etu.umontpellier.fr"
__status__ = "Development"
import Rotor


class ETW(Rotor.Rotor):
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