import enum


class VerteilerArt(str, enum.Enum):
    ESTW = "ESTW"
    RSTW = "RSTW"
    KS = "KS"
    MST = "MST"


class ElementArt(str, enum.Enum):
    Hp = "Hp"
    Vs = "Vs"
    VW = "VW"
    Ls = "Ls"
    Az = "Az"
    PZB = "PZB"
    GU = "GÜ"


class DokumentTyp(str, enum.Enum):
    KUEP = "KÜP"
    VLP = "VLP"


class DokumentStatus(str, enum.Enum):
    IMPORTIERT = "importiert"
    ANALYSIERT = "analysiert"
    FEHLER = "fehler"
    ARCHIVIERT = "archiviert"


class ObjektTyp(str, enum.Enum):
    VERTEILER = "verteiler"
    KABEL = "kabel"
    ELEMENT = "element"
