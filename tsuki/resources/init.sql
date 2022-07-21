CREATE TABLE IF NOT EXISTS t_users (
    email       VARCHAR(320)    UNIQUE NOT NULL,
    username    VARCHAR(32)     PRIMARY KEY,
    password    VARCHAR(64)     NOT NULL,
    verified    BOOL            NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL
);

CREATE TABLE IF NOT EXISTS shorturl (
    token       VARCHAR(320)    PRIMARY KEY,
    id          CHAR(32)        UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    username    VARCHAR(32)     NOT NULL,
    id          CHAR(32)        PRIMARY KEY,
    body        VARCHAR(320)    NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL,
    CONSTRAINT fk_username
        FOREIGN KEY(username)
            REFERENCES t_users(username)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS follows (
    username    VARCHAR(32)     NOT NULL,
    following   VARCHAR(32)     NOT NULL,
    CONSTRAINT fk_username
        FOREIGN KEY(username)
            REFERENCES t_users(username)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
    CONSTRAINT fk_following
        FOREIGN KEY(following)
            REFERENCES t_users(username)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS votes (
    id          CHAR(32)        NOT NULL,
    username    VARCHAR(32)     NOT NULL,
    CONSTRAINT fk_id
        FOREIGN KEY(id)
            REFERENCES posts(id)
            ON DELETE CASCADE,
    CONSTRAINT fk_username
        FOREIGN KEY(username)
            REFERENCES t_users(username)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    post_id     CHAR(32)        NOT NULL,
    comment_id  CHAR(32)        UNIQUE NOT NULL,
    username    VARCHAR(32)     NOT NULL,
    body        VARCHAR(320)    NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL,
    CONSTRAINT fk_post_id
        FOREIGN KEY(post_id)
            REFERENCES posts(id)
            ON DELETE CASCADE,
    CONSTRAINT fk_username
        FOREIGN KEY(username)
            REFERENCES t_users(username)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);
