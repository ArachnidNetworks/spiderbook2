CREATE TABLE posts (
    /* Post id */
    pid VARCHAR(25) NOT NULL UNIQUE,
    /* Post's category (works as a tag) */
    category VARCHAR(50) NOT NULL,
    /* Post's author */
    author VARCHAR(30) NOT NULL,
    /* Post's creation timestamp */
    postts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    /* Post title */
    title VARCHAR(80) NOT NULL,
    /* Post's text content */
    body TEXT,
    /* Post's binary content */
    imgbin BYTEA,
    /* Author's hashed IP address */
    poster_ip VARCHAR(40) NOT NULL DEFAULT 'NO_IP'
);