import enum

from sqlalchemy import Enum as SAEnum


class DistributorType(str, enum.Enum):
    ESTW = "ESTW"
    RSTW = "RSTW"
    KS = "KS"
    MST = "MST"


class ElementType(str, enum.Enum):
    HP = "Hp"
    VS = "Vs"
    VW = "VW"
    LS = "Ls"
    AZ = "Az"
    PZB = "PZB"
    GU = "GÜ"


class DocumentType(str, enum.Enum):
    KUEP = "KÜP"
    VLP = "VLP"


class DocumentStatus(str, enum.Enum):
    HOCHGELADEN = "hochgeladen"
    IN_VERARBEITUNG = "in_verarbeitung"
    VERARBEITET = "verarbeitet"
    FEHLER = "fehler"


class ObjectType(str, enum.Enum):
    VERTEILER = "verteiler"
    KABEL = "kabel"
    ELEMENT = "element"


distributor_type_enum = SAEnum(
    DistributorType, name="verteiler_art", native_enum=True, create_constraint=True
)
element_type_enum = SAEnum(
    ElementType, name="element_art", native_enum=True, create_constraint=True
)
document_type_enum = SAEnum(
    DocumentType, name="dokument_typ", native_enum=True, create_constraint=True
)
document_status_enum = SAEnum(
    DocumentStatus, name="dokument_status", native_enum=True, create_constraint=True
)
object_type_enum = SAEnum(
    ObjectType, name="objekt_typ", native_enum=True, create_constraint=True
)
