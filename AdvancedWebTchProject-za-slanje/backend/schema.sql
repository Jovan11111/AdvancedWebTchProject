CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

CREATE TABLE book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(160) NOT NULL,
    description TEXT NOT NULL,
    isbn VARCHAR(40) NOT NULL,
    image_filename VARCHAR(255) NOT NULL DEFAULT 'placeholder_book_cover.jpeg'
);

CREATE TABLE reading_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES user(id),
    book_id INTEGER NOT NULL REFERENCES book(id),
    status VARCHAR(30) NOT NULL DEFAULT 'not_read',
    updated_at DATETIME,
    UNIQUE(user_id, book_id)
);

CREATE TABLE friendship (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id INTEGER NOT NULL REFERENCES user(id),
    following_id INTEGER NOT NULL REFERENCES user(id),
    created_at DATETIME,
    UNIQUE(follower_id, following_id)
);