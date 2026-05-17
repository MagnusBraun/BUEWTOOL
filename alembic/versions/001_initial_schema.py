"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    objekt_typ = postgresql.ENUM(
        "verteiler", "kabel", "element", name="objekt_typ", create_type=True
    )
    verteiler_art = postgresql.ENUM(
        "ESTW", "RSTW", "KS", "MST", name="verteiler_art", create_type=True
    )
    element_art = postgresql.ENUM(
        "Hp", "Vs", "VW", "Ls", "Az", "PZB", "GÜ", name="element_art", create_type=True
    )
    dokument_typ = postgresql.ENUM("KÜP", "VLP", name="dokument_typ", create_type=True)
    dokument_status = postgresql.ENUM(
        "importiert",
        "analysiert",
        "fehler",
        "archiviert",
        name="dokument_status",
        create_type=True,
    )

    op.create_table(
        "projekte",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "objekte",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "projekt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projekte.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("objekt_typ", objekt_typ, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("idx_objekte_projekt_typ", "objekte", ["projekt_id", "objekt_typ"])

    op.create_table(
        "dokumente",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "projekt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projekte.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("dokumenttyp", dokument_typ, nullable=False),
        sa.Column("dateiname", sa.String(512), nullable=False),
        sa.Column("dateipfad", sa.Text(), nullable=False),
        sa.Column(
            "importdatum",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "status",
            dokument_status,
            nullable=False,
            server_default="importiert",
        ),
        sa.Column("metadaten", postgresql.JSONB(), server_default="{}"),
    )
    op.create_index("idx_dokumente_projekt", "dokumente", ["projekt_id"])

    op.create_table(
        "verteiler",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("objekte.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("art", verteiler_art, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("km", sa.Numeric(10, 3)),
        sa.Column("str", sa.Integer()),
        sa.Column("bemerkungen", sa.Text()),
        sa.Column("bbox_x", sa.Float()),
        sa.Column("bbox_y", sa.Float()),
        sa.Column("bbox_breite", sa.Float()),
        sa.Column("bbox_hoehe", sa.Float()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "kabel",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("objekte.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("typ", sa.String(64)),
        sa.Column("index", sa.String(16)),
        sa.Column("durchmesser", sa.String(32)),
        sa.Column("trommelnummer", sa.String(64)),
        sa.Column(
            "von_ort_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("verteiler.id", ondelete="SET NULL"),
        ),
        sa.Column(
            "bis_ort_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("verteiler.id", ondelete="SET NULL"),
        ),
        sa.Column("von_km", sa.Numeric(10, 3)),
        sa.Column("von_metrierung", sa.String(64)),
        sa.Column("bis_km", sa.Numeric(10, 3)),
        sa.Column("bis_metrierung", sa.String(64)),
        sa.Column("laenge_soll", sa.Numeric(10, 2)),
        sa.Column("laenge_ist", sa.Numeric(10, 2)),
        sa.Column("verlegeart", sa.String(64)),
        sa.Column("vlp_nummer", sa.String(64)),
        sa.Column("bemerkungen", sa.Text()),
        sa.Column("str", sa.Integer()),
        sa.Column("streckenuebergreifend", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("geom_line", postgresql.JSONB()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("idx_kabel_name", "kabel", ["name"])
    op.create_index("idx_kabel_von", "kabel", ["von_ort_id"])
    op.create_index("idx_kabel_bis", "kabel", ["bis_ort_id"])
    op.create_index("idx_kabel_str", "kabel", ["str"])

    op.create_table(
        "elemente",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("objekte.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("elementart", element_art, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column(
            "kabel_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kabel.id", ondelete="SET NULL"),
        ),
        sa.Column(
            "verteiler_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("verteiler.id", ondelete="SET NULL"),
        ),
        sa.Column("str", sa.Integer()),
        sa.Column("bemerkungen", sa.Text()),
        sa.Column("bbox_x", sa.Float()),
        sa.Column("bbox_y", sa.Float()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("idx_elemente_kabel", "elemente", ["kabel_id"])
    op.create_index("idx_elemente_str", "elemente", ["str"])

    op.create_table(
        "annotationen",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dokument_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dokumente.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "objekt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("objekte.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("breite", sa.Float()),
        sa.Column("hoehe", sa.Float()),
        sa.Column("text", sa.Text()),
        sa.Column("farbe", sa.String(32)),
        sa.Column("erstellt_von", sa.String(128)),
        sa.Column(
            "erstellt_am",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("idx_annotationen_dokument", "annotationen", ["dokument_id"])
    op.create_index("idx_annotationen_objekt", "annotationen", ["objekt_id"])

    op.create_table(
        "historie",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "objekt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("objekte.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("feld", sa.String(64), nullable=False),
        sa.Column("alter_wert", sa.Text()),
        sa.Column("neuer_wert", sa.Text()),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("benutzer", sa.String(128)),
    )
    op.create_index("idx_historie_objekt", "historie", ["objekt_id", "timestamp"])

    op.create_table(
        "vlp_import_zeilen",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dokument_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dokumente.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kabel_name", sa.String(64)),
        sa.Column("laenge_ist", sa.Numeric(10, 2)),
        sa.Column("trommelnummer", sa.String(64)),
        sa.Column("verlegeart", sa.String(64)),
        sa.Column("vlp_nummer", sa.String(64)),
        sa.Column("rohdaten", postgresql.JSONB()),
        sa.Column(
            "matched_kabel_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kabel.id", ondelete="SET NULL"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("idx_kabel_name_lookup", "kabel", ["name"], unique=False)


def downgrade() -> None:
    op.drop_table("vlp_import_zeilen")
    op.drop_table("historie")
    op.drop_table("annotationen")
    op.drop_table("elemente")
    op.drop_table("kabel")
    op.drop_table("verteiler")
    op.drop_table("dokumente")
    op.drop_table("objekte")
    op.drop_table("projekte")

    for enum_name in (
        "dokument_status",
        "dokument_typ",
        "element_art",
        "verteiler_art",
        "objekt_typ",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
