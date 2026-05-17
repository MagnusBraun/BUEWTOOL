-- LST Bauüberwachung – PostgreSQL-Referenzschema
-- Ausführung: psql -U postgres -d lst_bauueberwachung -f database/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
CREATE TYPE verteiler_art AS ENUM ('ESTW', 'RSTW', 'KS', 'MST');
CREATE TYPE element_art AS ENUM ('Hp', 'Vs', 'VW', 'Ls', 'Az', 'PZB', 'GÜ');
CREATE TYPE dokument_typ AS ENUM ('KÜP', 'VLP');
CREATE TYPE dokument_status AS ENUM ('hochgeladen', 'in_verarbeitung', 'verarbeitet', 'fehler');
CREATE TYPE objekt_typ AS ENUM ('verteiler', 'kabel', 'element');

-- Verteiler (ESTW, RSTW, KS, Signalmast)
CREATE TABLE verteiler (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    art             verteiler_art NOT NULL,
    name            VARCHAR(255) NOT NULL,
    km              NUMERIC(10, 3),
    str             INTEGER,
    bemerkungen     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_verteiler_art_name UNIQUE (art, name)
);

CREATE INDEX idx_verteiler_str ON verteiler (str);
CREATE INDEX idx_verteiler_km ON verteiler (km);

-- Kabel (zentrale Entität, einmalig pro Name)
CREATE TABLE kabel (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    VARCHAR(64) NOT NULL,
    typ                     VARCHAR(128),
    index                   VARCHAR(32),
    durchmesser             VARCHAR(64),
    trommelnummer           VARCHAR(64),
    von_verteiler_id        UUID REFERENCES verteiler (id) ON DELETE SET NULL,
    bis_verteiler_id        UUID REFERENCES verteiler (id) ON DELETE SET NULL,
    von_ort                 VARCHAR(255),
    von_km                  NUMERIC(10, 3),
    von_metrierung          VARCHAR(64),
    bis_ort                 VARCHAR(255),
    bis_km                  NUMERIC(10, 3),
    bis_metrierung          VARCHAR(64),
    laenge_soll             NUMERIC(10, 2),
    laenge_ist              NUMERIC(10, 2),
    verlegeart              VARCHAR(128),
    vlp_nummer              VARCHAR(64),
    bemerkungen             TEXT,
    str                     INTEGER,
    streckenuebergreifend  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_kabel_name UNIQUE (name)
);

CREATE INDEX idx_kabel_str ON kabel (str);
CREATE INDEX idx_kabel_von_verteiler ON kabel (von_verteiler_id);
CREATE INDEX idx_kabel_bis_verteiler ON kabel (bis_verteiler_id);

-- Elemente (Signale, Achszähler, …)
CREATE TABLE elemente (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    elementart      element_art NOT NULL,
    name            VARCHAR(255) NOT NULL,
    kabel_id        UUID REFERENCES kabel (id) ON DELETE SET NULL,
    verteiler_id    UUID REFERENCES verteiler (id) ON DELETE SET NULL,
    str             INTEGER,
    bemerkungen     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_element_art_name UNIQUE (elementart, name)
);

CREATE INDEX idx_elemente_kabel ON elemente (kabel_id);
CREATE INDEX idx_elemente_verteiler ON elemente (verteiler_id);
CREATE INDEX idx_elemente_str ON elemente (str);

-- Dokumente (KÜP, VLP)
CREATE TABLE dokumente (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokumenttyp     dokument_typ NOT NULL,
    dateiname       VARCHAR(512) NOT NULL,
    dateipfad       VARCHAR(1024) NOT NULL,
    importdatum     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status          dokument_status NOT NULL DEFAULT 'hochgeladen',
    fehlermeldung   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_dokumente_typ ON dokumente (dokumenttyp);
CREATE INDEX idx_dokumente_status ON dokumente (status);

-- Annotationen auf Plänen
CREATE TABLE annotationen (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dokument_id     UUID NOT NULL REFERENCES dokumente (id) ON DELETE CASCADE,
    objekt_typ      objekt_typ NOT NULL,
    objekt_id       UUID NOT NULL,
    seite           INTEGER NOT NULL DEFAULT 1,
    x               DOUBLE PRECISION NOT NULL,
    y               DOUBLE PRECISION NOT NULL,
    breite          DOUBLE PRECISION NOT NULL,
    hoehe           DOUBLE PRECISION NOT NULL,
    text            TEXT,
    farbe           VARCHAR(32),
    erstellt_von    VARCHAR(255),
    erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_annotationen_dokument ON annotationen (dokument_id);
CREATE INDEX idx_annotationen_objekt ON annotationen (objekt_typ, objekt_id);

-- Änderungshistorie (audit trail)
CREATE TABLE historie (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objekt_typ      objekt_typ NOT NULL,
    objekt_id       UUID NOT NULL,
    feld            VARCHAR(128) NOT NULL,
    alter_wert      TEXT,
    neuer_wert      TEXT,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    benutzer        VARCHAR(255) NOT NULL DEFAULT 'system'
);

CREATE INDEX idx_historie_objekt ON historie (objekt_typ, objekt_id);
CREATE INDEX idx_historie_timestamp ON historie (timestamp DESC);

-- Trigger: updated_at automatisch setzen
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verteiler_updated_at
    BEFORE UPDATE ON verteiler
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_kabel_updated_at
    BEFORE UPDATE ON kabel
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_elemente_updated_at
    BEFORE UPDATE ON elemente
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_dokumente_updated_at
    BEFORE UPDATE ON dokumente
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
