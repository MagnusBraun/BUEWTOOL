"""Initial schema for LST Bauüberwachung.

Revision ID: 001
Revises:
Create Date: 2026-05-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

verteiler_art = postgresql.ENUM("ESTW", "RSTW", "KS", "MST", name="verteiler_art", create_type=False)
element_art = postgresql.ENUM("Hp", "Vs", "VW", "Ls", "Az", "PZB", "GÜ", name="element_art", create_type=False)
dokument_typ = postgresql.ENUM("KÜP", "VLP", name="dokument_typ", create_type=False)
dokument_status = postgresql.ENUM(
    "hochgeladen", "in_verarbeitung", "verarbeitet", "fehler", name="dokument_status", create_type=False
)
objekt_typ = postgresql.ENUM("verteiler", "kabel", "element", name="objekt_typ", create_type=False)


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    verteiler_art.create(op.get_bind(), checkfirst=True)
    element_art.create(op.get_bind(), checkfirst=True)
    dokument_typ.create(op.get_bind(), checkfirst=True)
    dokument_status.create(op.get_bind(), checkfirst=True)
    objekt_typ.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "verteiler",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("art", verteiler_art, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("km", sa.Numeric(10, 3), nullable=True),
        sa.Column("str", sa.Integer(), nullable=True),
        sa.Column("bemerkungen", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("art", "name", name="uq_verteiler_art_name"),
    )
    op.create_index("idx_verteiler_str", "verteiler", ["str"])
    op.create_index("idx_verteiler_km", "verteiler", ["km"])

    op.create_table(
        "kabel",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("typ", sa.String(128), nullable=True),
        sa.Column("index", sa.String(32), nullable=True),
        sa.Column("durchmesser", sa.String(64), nullable=True),
        sa.Column("trommelnummer", sa.String(64), nullable=True),
        sa.Column("von_verteiler_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verteiler.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bis_verteiler_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verteiler.id", ondelete="SET NULL"), nullable=True),
        sa.Column("von_ort", sa.String(255), nullable=True),
        sa.Column("von_km", sa.Numeric(10, 3), nullable=True),
        sa.Column("von_metrierung", sa.String(64), nullable=True),
        sa.Column("bis_ort", sa.String(255), nullable=True),
        sa.Column("bis_km", sa.Numeric(10, 3), nullable=True),
        sa.Column("bis_metrierung", sa.String(64), nullable=True),
        sa.Column("laenge_soll", sa.Numeric(10, 2), nullable=True),
        sa.Column("laenge_ist", sa.Numeric(10, 2), nullable=True),
        sa.Column("verlegeart", sa.String(128), nullable=True),
        sa.Column("vlp_nummer", sa.String(64), nullable=True),
        sa.Column("bemerkungen", sa.Text(), nullable=True),
        sa.Column("str", sa.Integer(), nullable=True),
        sa.Column("streckenuebergreifend", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_kabel_name"),
    )
    op.create_index("idx_kabel_str", "kabel", ["str"])
    op.create_index("idx_kabel_von_verteiler", "kabel", ["von_verteiler_id"])
    op.create_index("idx_kabel_bis_verteiler", "kabel", ["bis_verteiler_id"])

    op.create_table(
        "elemente",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("elementart", element_art, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("kabel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kabel.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verteiler_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verteiler.id", ondelete="SET NULL"), nullable=True),
        sa.Column("str", sa.Integer(), nullable=True),
        sa.Column("bemerkungen", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("elementart", "name", name="uq_element_art_name"),
    )
    op.create_index("idx_elemente_kabel", "elemente", ["kabel_id"])
    op.create_index("idx_elemente_verteiler", "elemente", ["verteiler_id"])
    op.create_index("idx_elemente_str", "elemente", ["str"])

    op.create_table(
        "dokumente",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("dokumenttyp", dokument_typ, nullable=False),
        sa.Column("dateiname", sa.String(512), nullable=False),
        sa.Column("dateipfad", sa.String(1024), nullable=False),
        sa.Column("importdatum", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("status", dokument_status, server_default="hochgeladen", nullable=False),
        sa.Column("fehlermeldung", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_dokumente_typ", "dokumente", ["dokumenttyp"])
    op.create_index("idx_dokumente_status", "dokumente", ["status"])

    op.create_table(
        "annotationen",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("dokument_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dokumente.id", ondelete="CASCADE"), nullable=False),
        sa.Column("objekt_typ", objekt_typ, nullable=False),
        sa.Column("objekt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seite", sa.Integer(), server_default="1", nullable=False),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("breite", sa.Float(), nullable=False),
        sa.Column("hoehe", sa.Float(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("farbe", sa.String(32), nullable=True),
        sa.Column("erstellt_von", sa.String(255), nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_annotationen_dokument", "annotationen", ["dokument_id"])
    op.create_index("idx_annotationen_objekt", "annotationen", ["objekt_typ", "objekt_id"])

    op.create_table(
        "historie",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("objekt_typ", objekt_typ, nullable=False),
        sa.Column("objekt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feld", sa.String(128), nullable=False),
        sa.Column("alter_wert", sa.Text(), nullable=True),
        sa.Column("neuer_wert", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("benutzer", sa.String(255), server_default="system", nullable=False),
    )
    op.create_index("idx_historie_objekt", "historie", ["objekt_typ", "objekt_id"])
    op.create_index("idx_historie_timestamp", "historie", ["timestamp"])

    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    for table in ("verteiler", "kabel", "elemente", "dokumente"):
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """)


def downgrade() -> None:
    for table in ("dokumente", "elemente", "kabel", "verteiler"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table}")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")

    op.drop_table("historie")
    op.drop_table("annotationen")
    op.drop_table("dokumente")
    op.drop_table("elemente")
    op.drop_table("kabel")
    op.drop_table("verteiler")

    objekt_typ.drop(op.get_bind(), checkfirst=True)
    dokument_status.drop(op.get_bind(), checkfirst=True)
    dokument_typ.drop(op.get_bind(), checkfirst=True)
    element_art.drop(op.get_bind(), checkfirst=True)
    verteiler_art.drop(op.get_bind(), checkfirst=True)
