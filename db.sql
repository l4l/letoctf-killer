CREATE TABLE info (
    tg_id INTEGER PRIMARY KEY,
    pass TEXT,
    last_try INTEGER
);

CREATE TABLE names (
    fio TEXT,
    pass TEXT PRIMARY KEY
);

CREATE TABLE aims (
    user_pass TEXT PRIMARY KEY,
    aim TEXT
);

CREATE TABLE kills (
    pass TEXT,
    killed_pass TEXT,
    tm INTEGER
);

.mode csv
.import codes.dat names
.import aims.dat aims