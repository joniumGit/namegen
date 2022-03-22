CREATE TABLE IF NOT EXISTS start
(
    id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    value VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS end
(
    id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    value VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sequences
(
    start_id   INTEGER NOT NULL,
    end_id     INTEGER NOT NULL,
    next_value INTEGER NOT NULL DEFAULT (ABS(RANDOM() % 10000)),
    count      INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (start_id, end_id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS state
(
    current_count INTEGER NOT NULL DEFAULT 0,
    next_start_id INTEGER NOT NULL DEFAULT 1,
    next_end_id   INTEGER NOT NULL DEFAULT 1
);

INSERT INTO state DEFAULT
VALUES;

INSERT INTO start (value)
VALUES ('golden'),
       ('slow'),
       ('lovely'),
       ('lucky'),
       ('fine'),
       ('clever'),
       ('quiet'),
       ('calm'),
       ('sturdy'),
       ('courageous'),
       ('fast'),
       ('confident'),
       ('bright'),
       ('lively'),
       ('friendly'),
       ('cool'),
       ('awesome');

INSERT INTO end (value)
VALUES ('adventurer'),
       ('hero'),
       ('squirrel'),
       ('butterfly'),
       ('scientist'),
       ('fellow'),
       ('hedgehog'),
       ('fox'),
       ('wolf'),
       ('bear'),
       ('fish'),
       ('swan'),
       ('owl'),
       ('player'),
       ('whale'),
       ('crow');

INSERT INTO sequences (start_id, end_id)
SELECT s.id, e.id
FROM start s
         CROSS JOIN end e;
