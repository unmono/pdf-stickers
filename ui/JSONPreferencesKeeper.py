import json
import tkinter
import os
from pathlib import Path
from typing import Callable, Any


class JSONPreferencesKeeper:
    """
    Provide methods to store subclass' attributes in JSON file, retrieve and set them up
    Call define_preps method, give it attributes names in strings and optionally path to
    the file where to store them.

    To deal with special instances, that should or must be converted(e.g. unserializable
    instances), override convert_prefs_functions method to update or change completely
    the mapping of types to converter functions for instances of those types.

    Originally it maps this types: [tkinter.Variable, os.PathLike]. Instances of other
    types will be stored as is, if possible.

    Basic usage:

    define_prefs('attribute', 'names', 'that', 'we', 'want', 'to', 'store') - after
    initialization

    save_prefs() - to store preferences

    set_prefs() - to retrieve and set those attributes
    """
    _preferences: tuple[str]
    _preferences_file: Path

    def convert_prefs_functions(self) -> dict[any, tuple[Callable, Callable]]:
        """
        Return dictionary, that maps types to converter functions.
        It is needed to store unseralizable values or if some values
        should be converted before storing. The first function is used to convert
        value to store it, the second one - to deconvert from storage and set it.

        For example, if it's needed to store strings in the uppercase, but use them
        in lowercase(why not?), one entry of this dictionary would be:
        :return: {str: (lambda value: value.upper(), lambda name, obj, value: setattr(self, name, value.lower()}
        """
        return {
            tkinter.Variable: (lambda p: p.get(), lambda _, obj, val: obj.set(val)),
            os.PathLike: (lambda p: str(Path(p).resolve()), lambda name, _, val: setattr(self, name, Path(val))),
        }

    def convert_prefs(self, value):
        """
        Use defined functions mapped to types to convert values of these types.
        If value has a type not listed in dictionary, it will be returned as is.
        :param value: value of preference to store
        :return: converted value
        """
        cf = self.convert_prefs_functions()
        for pref_type, convert_function in cf.items():
            if isinstance(value, pref_type):
                return convert_function[0](value)
        return value

    def deconvert_prefs(self, attr_name: str, attr_instance: Any, stored_value: str):
        """

        """
        cf = self.convert_prefs_functions()
        for pref_type, convert_function in cf.items():
            if isinstance(attr_instance, pref_type):
                convert_function[1](attr_name, attr_instance, stored_value)
                return
        # todo: finish it

    def save_prefs(self) -> None:
        preferences_to_save = {}
        for p in self._preferences:
            value = getattr(self, p)
            if not value:
                continue
            preferences_to_save[p] = self.convert_prefs(value)

        self._preferences_file.touch()
        with self._preferences_file.open(mode='w') as f:
            json.dump(preferences_to_save, f)

    def set_prefs(self) -> None:
        if not self._preferences_file.exists():
            return
        with self._preferences_file.open(mode='r') as f:
            saved_preferences = json.load(f)
        for p in self._preferences:
            if p not in saved_preferences:
                continue
            attr_instance = getattr(self, p)
            self.deconvert_prefs(p, attr_instance, saved_preferences[p])

    # def set_prefs(self) -> None:
    #     if not self._preferences_file.exists():
    #         return
    #
    #     with self._preferences_file.open(mode='r') as f:
    #         saved_preferences = json.load(f)
    #
    #     for p in self._preferences:
    #         if p not in saved_preferences:
    #             continue
    #         value = getattr(self, p)
    #         if isinstance(value, tkinter.Variable):
    #             value.set(saved_preferences[p])
    #         elif isinstance(value, os.PathLike):
    #             pref_path = Path(saved_preferences[p])
    #             if pref_path.exists():
    #                 setattr(self, p, pref_path)
    #         else:
    #             setattr(self, p, saved_preferences[p])

    def define_prefs(self, *args: str, preferences_file: str | os.PathLike = 'preferences.json') -> None:
        for arg in args:
            if not isinstance(arg, str):
                raise AttributeError('All attribute names should be strings')
            if not hasattr(self, arg):
                raise AttributeError(f'No such attribute \'{arg}\'')

        self._preferences = args
        self._preferences_file = Path(preferences_file)
