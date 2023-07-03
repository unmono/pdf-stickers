import json
import tkinter
import os
from pathlib import Path


class JSONPreferencesKeeper:
    _preferences: tuple[str]
    _preferences_file: Path

    def save_prefs(self) -> None:
        preferences_to_save = {}
        for p in self._preferences:
            value = getattr(self, p)
            if not value:
                continue

            if isinstance(value, tkinter.Variable):
                value_to_save = value.get()
            elif isinstance(value, os.PathLike):
                value_to_save = str(Path(value).resolve())
            else:
                value_to_save = value

            preferences_to_save[p] = value_to_save

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
            value = getattr(self, p)
            if isinstance(value, tkinter.Variable):
                value.set(saved_preferences[p])
            elif isinstance(value, os.PathLike):
                pref_path = Path(saved_preferences[p])
                if pref_path.exists():
                    setattr(self, p, pref_path)
            else:
                setattr(self, p, saved_preferences[p])

    def define_prefs(self, *args: str, preferences_file: str | os.PathLike = 'preferences.json') -> None:
        for arg in args:
            if not isinstance(arg, str):
                raise AttributeError('All attribute names should be strings')
            if not hasattr(self, arg):
                raise AttributeError(f'No such attribute \'{arg}\'')

        self._preferences = args
        self._preferences_file = Path(preferences_file)
