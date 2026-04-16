"""Partition table inspector for MBR and GPT images."""

from __future__ import annotations

import argparse
import platform
import struct
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

from uuid_types import GptType

SECTOR_SIZE = 512
GPT_ENTRY_SIZE = 128
GPT_ENTRY_COUNT = 128


class Disk(Enum):
    Linux = "/dev/sda"
    Windows = r"\\.\physicaldrive0"
    Darwin = "/dev/disk0"


class PType(Enum):
    WIN = 0x07
    WIN_EXTENDED = 0x0F
    LINUX_SWAP = 0x82
    LINUX = 0x83
    GPT = 0xEE
    EMPTY = 0x00


@dataclass
class Partition:
    boot: str
    type: PType
    start: int
    size: int

    @classmethod
    def factory(cls, entry: bytes) -> "Partition":
        boot_flag = entry[0]
        type_code = entry[4]
        start_lba = struct.unpack_from("<I", entry, 8)[0]
        size_lba = struct.unpack_from("<I", entry, 12)[0]
        boot = "boot" if boot_flag == 0x80 else ""
        try:
            partition_type = PType(type_code)
        except ValueError:
            partition_type = PType.EMPTY
        return cls(boot, partition_type, start_lba * SECTOR_SIZE, size_lba * SECTOR_SIZE)

    @staticmethod
    def convert(n: int) -> str:
        if n < 1_000:
            return f"{n}B"
        if n < 1_000_000:
            return f"{n / 1_000:.1f}K"
        if n < 1_000_000_000:
            return f"{n / 1_000_000:.1f}M"
        return f"{n / 1_000_000_000:.1f}G"

    def __str__(self) -> str:
        return (
            f"{Partition.convert(self.start):<10s}"
            f"{Partition.convert(self.size):<15s}"
            f"{self.type.name:<15s}"
            f"{self.boot:<10s}"
        )

    def is_gpt(self) -> bool:
        return self.type == PType.GPT


class PartitionGPT:
    table_gpt: List["PartitionGPT"] = []

    def __init__(self, entry: bytes) -> None:
        self.type_guid = uuid.UUID(bytes_le=entry[0:16])
        self.start_lba, self.end_lba = struct.unpack_from("<QQ", entry, 32)
        self.start = self.start_lba * SECTOR_SIZE
        self.size = (self.end_lba - self.start_lba + 1) * SECTOR_SIZE
        try:
            self.name = GptType(self.type_guid).name
        except ValueError:
            self.name = str(self.type_guid)

    def __str__(self) -> str:
        return f"{Partition.convert(self.start):<10s}{Partition.convert(self.size):<15s}{self.name:<15s}"


class Mbr:
    def __init__(self, disk: str | Path) -> None:
        self.disk = str(disk)
        with open(self.disk, "rb") as f:
            self.mbr = f.read(SECTOR_SIZE)
            self.magic = struct.unpack_from("<H", self.mbr, 510)[0]

    def is_mbr(self) -> bool:
        return self.magic == 0xAA55

    def _load_gpt_table(self) -> None:
        if PartitionGPT.table_gpt:
            return

        with open(self.disk, "rb") as f:
            f.seek(SECTOR_SIZE * 2)
            data = f.read(GPT_ENTRY_SIZE * GPT_ENTRY_COUNT)

        for offset in range(0, len(data), GPT_ENTRY_SIZE):
            entry = data[offset : offset + GPT_ENTRY_SIZE]
            if not entry.strip(b"\x00"):
                continue
            PartitionGPT.table_gpt.append(PartitionGPT(entry))

    def partitions(self) -> None:
        if not self.is_mbr():
            raise ValueError(f"{self.disk} does not contain a valid MBR signature")

        table: List[Partition] = []
        for offset in range(446, 446 + 16 * 4, 16):
            table.append(Partition.factory(self.mbr[offset : offset + 16]))

        print(f'{"Start":<10s}{"Size":<15s}{"File System":<15s}{"Boot":<10s}')
        for partition in table:
            if partition.type == PType.EMPTY:
                continue
            if partition.is_gpt():
                self._load_gpt_table()
                for partition_gpt in PartitionGPT.table_gpt:
                    print(partition_gpt)
                return
            print(partition)

    def disksize(self) -> str:
        if not PartitionGPT.table_gpt:
            self._load_gpt_table()
        total = sum(p.size for p in PartitionGPT.table_gpt)
        return Partition.convert(total)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect MBR/GPT partition tables.")
    default_disk = Disk[platform.system()].value if platform.system() in Disk.__members__ else Disk.Linux.value
    parser.add_argument("disk", nargs="?", default=default_disk, help="Disk image or block device path")
    args = parser.parse_args()

    mbr = Mbr(args.disk)
    mbr.partitions()
    if PartitionGPT.table_gpt:
        print(f"{mbr.disk}  {mbr.disksize()}")


if __name__ == "__main__":
    main()