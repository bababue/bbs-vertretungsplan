CREATE TABLE aktuell (
    id  SERIAL PRIMARY KEY,
    datum DATE NOT NULL,
    stunde INTEGER,
    stunde_2 INTEGER,
    kurs VARCHAR(50) NOT NULL,
    raum VARCHAR(50),
    raum_ersatz VARCHAR(50),
    lehrer VARCHAR(50),
    lehrer_ersatz VARCHAR(50),
    typ VARCHAR(50),
    beschreibung VARCHAR(100)
);