"""GPT type GUID mapping used by the partition parser."""

from enum import Enum
import uuid


class GptType(Enum):
    Apple = uuid.UUID("ef57347c-0000-aa11-aa11-00306543ecac")
    EFI = uuid.UUID("28732ac1-1ff8-d211-ba4b-00a0c93ec93b")
    MicrosoftBasicData = uuid.UUID("a2a0d0eb-e5b9-3344-87c0-68b6b72699c7")
    MicrosoftReserved = uuid.UUID("16e3c9e3-5c0b-b84d-817d-f92df00215ae")
    WindowsRecoveryEnvironment = uuid.UUID("a4bb94de-d106-404d-a6a1-bfd50179d6ac")
    MicrosoftStorageSpace = uuid.UUID("8fafc5e7-80f6-ee4c-a3af-b001e56efc2d")
    LinuxFilesystem = uuid.UUID("af3dc60f-8384-7247-8e79-3d69d8477de4")
    LinuxRootPart = uuid.UUID("40954744-97f2-b241-f79a-d131d5f0458a")
    LinuxRootPartX86_64 = uuid.UUID("e3bc684f-cde8-b14d-e796-fbcaf984b709")
    LinuxSwapPart = uuid.UUID("6dfd5706-aba4-c443-e584-0933c84b4f4f")
    LinuxLVMPart = uuid.UUID("79d3d6e6-07f5-c244-3ca2-238f2a3df928")
    LinuxHomePart = uuid.UUID("e1c73a93-b42e-134f-44b8-0e14e2eef915")
    LinuxServerDataPart = uuid.UUID("25848f3b-e020-3b4f-7f90-1a25a76f98e8")
    LinuxReserved = uuid.UUID("3933a68d-0700-c060-36c4-083ac8230908")
