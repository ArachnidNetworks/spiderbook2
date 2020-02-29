CREATE TABLE idnumbers (
    idn INTEGER
);

INSERT INTO idnumbers (idn) VALUES (
    5
);

CREATE TABLE posts (
    uid VARCHAR(32) NOT NULL,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(80) NOT NULL,
    body_text VARCHAR(1000),
    body_file_url VARCHAR(500),
    ip VARCHAR(45) NOT NULL,
    dt TIMESTAMP NOT NULL,
    reply_uids VARCHAR(32)[]
);

CREATE TABLE replies (
    uid VARCHAR(32) NOT NULL,
    op_uid VARCHAR(32) NOT NULL,
    body_text VARCHAR(1000) NOT NULL,
    body_file_url VARCHAR(500),
    ip VARCHAR(45) NOT NULL,
    dt TIMESTAMP NOT NULL,
    reply_uids VARCHAR(32)[]
);

CREATE TABLE superusers (
    su_id VARCHAR(32) NOT NULL,
    su_type VARCHAR(3) NOT NULL,
    email VARCHAR(600) NOT NULL,
    password VARCHAR(256) NOT NULL,
    accepted BOOLEAN NOT NULL
);

CREATE TABLE banned (
    ip VARCHAR(45) NOT NULL,
    dt TIMESTAMP NOT NULL
);

