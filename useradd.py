"""Helper for provisioning a Linux user account."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import grp
import pwd
import subprocess
from typing import List, Tuple


ERRORS = {
    1: "Syntax Error {0} {1} {2}",
    2: "Argument {0} must be a string",
    3: "Argument {0} must not be empty",
}


@dataclass
class User:
    login: str
    password: str

    @classmethod
    def factory(cls, args: List[str]) -> "User | None":
        if cls.checkArguments(args):
            return cls(args[1], args[2])
        return None

    @staticmethod
    def checkArguments(args: List[str]) -> bool:
        if len(args) != 3:
            print(ERRORS[1].format(args[0], "login", "password"))
            return False
        if not isinstance(args[1], str):
            print(ERRORS[2].format(args[1]))
            return False
        if not args[1]:
            print(ERRORS[3].format(args[1]))
            return False
        if not isinstance(args[2], str):
            print(ERRORS[2].format(args[2]))
            return False
        if not args[2]:
            print(ERRORS[3].format(args[2]))
            return False
        return True

    @staticmethod
    def _first_free_id(used_ids: set[int], start: int = 1000) -> int:
        for candidate in range(start, 65535):
            if candidate not in used_ids:
                return candidate
        raise RuntimeError("No free identifier available")

    def _resolve_ids(self) -> Tuple[int, int, bool]:
        used_uids = {entry.pw_uid for entry in pwd.getpwall()}
        used_gids = {entry.gr_gid for entry in grp.getgrall()}

        uid = self._first_free_id(used_uids)
        try:
            gid = grp.getgrnam(self.login).gr_gid
            group_exists = True
        except KeyError:
            gid = self._first_free_id(used_gids)
            group_exists = False

        return uid, gid, group_exists

    def build_plan(self) -> list[list[str]]:
        uid, gid, group_exists = self._resolve_ids()
        plan: list[list[str]] = []
        if not group_exists:
            plan.append(["sudo", "groupadd", "--gid", str(gid), self.login])
        plan.append(
            [
                "sudo",
                "useradd",
                "--uid",
                str(uid),
                "--gid",
                str(gid),
                "--create-home",
                "--home-dir",
                f"/home/{self.login}",
                "--shell",
                "/bin/bash",
                self.login,
            ]
        )
        plan.append(["sudo", "chpasswd"])
        return plan

    def show_plan(self) -> None:
        for command in self.build_plan():
            print(" ".join(command))

    def apply(self) -> None:
        try:
            pwd.getpwnam(self.login)
            raise ValueError(f"User '{self.login}' already exists")
        except KeyError:
            pass

        uid, gid, group_exists = self._resolve_ids()
        if not group_exists:
            subprocess.run(["sudo", "groupadd", "--gid", str(gid), self.login], check=True)

        subprocess.run(
            [
                "sudo",
                "useradd",
                "--uid",
                str(uid),
                "--gid",
                str(gid),
                "--create-home",
                "--home-dir",
                f"/home/{self.login}",
                "--shell",
                "/bin/bash",
                self.login,
            ],
            check=True,
        )
        subprocess.run(
            ["sudo", "chpasswd"],
            input=f"{self.login}:{self.password}\n".encode(),
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision a Linux user account.")
    parser.add_argument("login", help="User login")
    parser.add_argument("password", help="User password")
    parser.add_argument("--apply", action="store_true", help="Execute the commands instead of previewing them")
    args = parser.parse_args()

    user = User(args.login, args.password)
    if args.apply:
        user.apply()
        print(f"User '{user.login}' has been created successfully.")
    else:
        print("Dry-run plan:")
        user.show_plan()


if __name__ == "__main__":
    main()