"""Create sparse disk images and attach them to loop devices."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import re
import shutil
import subprocess
from pathlib import Path
from typing import List


ERRORS = {
    1: "Syntax Error {0} {1} {2}",
    2: "Argument {0} must be a number",
    3: "Argument {0} must be as digit+[MGT]",
}

SIZE_MULTIPLIERS = {
    "M": 10**6,
    "G": 10**9,
    "T": 10**12,
}


@dataclass
class VirtualDisk:
    number: int
    size: str

    @classmethod
    def factory(cls, args: List[str]) -> "VirtualDisk | None":
        if cls.checkArguments(args):
            return cls(int(args[1]), args[2])
        return None

    @staticmethod
    def checkArguments(args: List[str]) -> bool:
        if len(args) != 3:
            print(ERRORS[1].format(args[0], "number", "size"))
            return False
        if not args[1].isdigit():
            print(ERRORS[2].format(args[1]))
            return False
        if not re.fullmatch(r"\d+[MGT]", args[2]):
            print(ERRORS[3].format(args[2]))
            return False
        return True

    def _size_to_bytes(self) -> int:
        unit = self.size[-1]
        value = int(self.size[:-1])
        return value * SIZE_MULTIPLIERS[unit]

    def checkFreeSpace(self) -> bool:
        required = self.number * self._size_to_bytes()
        free_bytes = shutil.disk_usage(Path.cwd()).free
        return free_bytes > required + 1_000_000

    def createVirtualDisks(self) -> List[Path]:
        if not self.checkFreeSpace():
            raise RuntimeError("Insufficient free space to create virtual disks")

        disk_dir = Path.cwd() / "virtual_disks"
        disk_dir.mkdir(exist_ok=True)

        created_images: List[Path] = []
        size_bytes = self._size_to_bytes()

        for index in range(1, self.number + 1):
            disk_file = disk_dir / f"disk{index}.img"
            with open(disk_file, "wb") as handle:
                handle.truncate(size_bytes)

            result = subprocess.run(
                ["sudo", "losetup", "--find", "--show", str(disk_file)],
                capture_output=True,
                text=True,
                check=True,
            )
            loop_device = result.stdout.strip()
            print(f"Created {disk_file} on {loop_device}")
            created_images.append(disk_file)

        return created_images


def main() -> None:
    parser = argparse.ArgumentParser(description="Create sparse virtual disks and attach them to loop devices.")
    parser.add_argument("number", help="Number of disks to create")
    parser.add_argument("size", help="Disk size, for example 10M, 2G or 1T")
    parser.add_argument("--apply", action="store_true", help="Actually create the disks instead of previewing")
    args = parser.parse_args()

    vd = VirtualDisk.factory(["vd_create.py", args.number, args.size])
    if vd is None:
        raise SystemExit(1)

    if args.apply:
        vd.createVirtualDisks()
    else:
        print(f"Dry-run: would create {vd.number} disk(s) of size {vd.size}")
        print(f"Dry-run: free space check = {vd.checkFreeSpace()}")


if __name__ == "__main__":
    main()
