CREATE TABLE comments (
    /* Comment id */
    pid VARCHAR(25) NOT NULL UNIQUE,
    /* Original post id (post or comment) */
    op_id VARCHAR(25) NOT NULL,
    /* Comment's author */
    author VARCHAR(30) NOT NULL,
    /* Comment's text content */
    content VARCHAR(300) NOT NULL,
    /* Comment's binary content */
    imgbin BYTEA,
    /* Author's hashed IP address */
    poster_ip VARCHAR(40) NOT NULL DEFAULT 'NO_IP'
);
