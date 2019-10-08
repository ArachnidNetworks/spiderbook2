/*
This file reproduces the PostgreSQL database used by the main application.
It creates a 'comments' table, a 'ids' table and a 'posts' table.
The comments table will store all the post comments, the 'ids' table will store the integer
that will be hashed for the next id, and the 'posts' table will store every single post.
*/

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

CREATE TABLE ids (
    v INTEGER NOT NULL
);
