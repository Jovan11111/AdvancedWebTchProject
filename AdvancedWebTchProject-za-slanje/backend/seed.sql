-- Aplikacija automatski dodaje ovaj seed pri prvom pokretanju.
-- Admin nalog: username=admin, password=admin123
INSERT INTO user (first_name, last_name, email, username, password_hash, role) VALUES
('System', 'Admin', 'admin@library.local', 'admin', 'scrypt:32768:8:1$vCzRjUqEuP5A7pZA$42bf401ce5ddedf7eabc0ec51941f2946636b42cf7057b30c6c9c54102f49f38164b9710f361091f46631c7b4e67c696419207f26242d674c2040ebbce0ff025', 'admin');

INSERT INTO book (title, author, description, isbn, image_filename) VALUES
('Na Drini ćuprija', 'Ivo Andrić', 'Roman o mostu i ljudima oko njega.', '978-86-10-00001-1', 'placeholder_book_cover.jpeg'),
('Mali princ', 'Antoine de Saint-Exupéry', 'Kratka priča o prijateljstvu, ljubavi i odgovornosti.', '978-86-10-00002-8', 'placeholder_book_cover.jpeg'),
('1984', 'George Orwell', 'Distopijski roman o nadzoru i slobodi.', '978-86-10-00003-5', 'placeholder_book_cover.jpeg'),
('Zločin i kazna', 'Fjodor Dostojevski', 'Roman o krivici, kazni i iskupljenju.', '978-86-10-00004-2', 'placeholder_book_cover.jpeg'),
('Gospodar prstenova', 'J. R. R. Tolkien', 'Epska avantura o putovanju i hrabrosti.', '978-86-10-00005-9', 'placeholder_book_cover.jpeg');