"""Application allowlist: only pre-approved applications may be launched.

The LLM never supplies a raw executable path. It supplies an alias
(e.g. "notepad", "browser") which is mapped here to a safe, fixed launch
target. Unknown aliases are rejected.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AllowedApplication:
    alias: str
    display_name: str
    windows_command: List[str]
    posix_command: List[str]


# Built-in safe aliases available out of the box on a normal Windows install.
_BUILTIN_APPS: Dict[str, AllowedApplication] = {
    "browser": AllowedApplication(
        alias="browser",
        display_name="Default Web Browser",
        windows_command=["cmd", "/c", "start", ""],
        posix_command=["xdg-open"],
    ),
    "calculator": AllowedApplication(
        alias="calculator",
        display_name="Calculator",
        windows_command=["calc.exe"],
        posix_command=["gnome-calculator"],
    ),
    "notepad": AllowedApplication(
        alias="notepad",
        display_name="Notepad",
        windows_command=["notepad.exe"],
        posix_command=["gedit"],
    ),
    "file explorer": AllowedApplication(
        alias="file explorer",
        display_name="File Explorer",
        windows_command=["explorer.exe"],
        posix_command=["xdg-open", "."],
    ),
}


def _normalise(alias: str) -> str:
    return alias.strip().lower()


class ApplicationAllowlist:
    """Merges built-in safe aliases with business apps from configuration.

    Configuration format for RIVA_ALLOWED_APPLICATIONS entries:
      "alias=display name|windows_exe_or_url"
    e.g. "myska pay=MYSKA Pay|https://app.myskapay.example.com"
           "novacore=NovaCore|C:\\Program Files\\NovaCore\\NovaCore.exe"
    """

    def __init__(self, configured_entries: List[str]):
        self._apps: Dict[str, AllowedApplication] = dict(_BUILTIN_APPS)
        for entry in configured_entries:
            app = self._parse_entry(entry)
            if app:
                self._apps[_normalise(app.alias)] = app

    @staticmethod
    def _parse_entry(entry: str) -> Optional[AllowedApplication]:
        if "=" not in entry:
            return None
        alias, rest = entry.split("=", 1)
        alias = alias.strip()
        if "|" in rest:
            display_name, target = rest.split("|", 1)
        else:
            display_name, target = rest, rest
        display_name = display_name.strip()
        target = target.strip()
        if target.lower().startswith(("http://", "https://")):
            windows_cmd = ["cmd", "/c", "start", "", target]
            posix_cmd = ["xdg-open", target]
        else:
            windows_cmd = [target]
            posix_cmd = [target]
        return AllowedApplication(
            alias=alias,
            display_name=display_name or alias,
            windows_command=windows_cmd,
            posix_command=posix_cmd,
        )

    def resolve(self, alias: str) -> Optional[AllowedApplication]:
        return self._apps.get(_normalise(alias))

    def list_apps(self) -> List[AllowedApplication]:
        return list(self._apps.values())

    def launch_command(self, alias: str) -> Optional[List[str]]:
        app = self.resolve(alias)
        if not app:
            return None
        return app.windows_command if sys.platform == "win32" else app.posix_command
