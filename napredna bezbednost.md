# Napredna bezbednost

U aplikaciji su implementirane sledeće bezbednosne provere:

## 1. Provera lozinke

Prilikom registracije i promene lozinke proverava se da lozinka:

- ima najmanje 8 karaktera;
- sadrži najmanje jedno veliko slovo;
- sadrži najmanje jedan broj.

Lozinke se ne čuvaju kao običan tekst, već kao zaštićene vrednosti.

## 2. Provera veličine slike

Prilikom dodavanja naslovnice knjige proverava se veličina slike.

Maksimalna dozvoljena veličina je **5 MB**. Ako je slika veća, aplikacija odbija unos i prikazuje poruku o grešci.

Naziv slike se dodatno obrađuje pomoću `secure_filename` funkcije pre čuvanja.

## 3. Zaštita od SQL injection napada

Podaci koje korisnik unosi ne ubacuju se direktno u SQL upite kao tekst.

Za pristup bazi koristi se SQLAlchemy ORM, koji automatski koristi parametrizovane upite. Na ovaj način korisnički unos se tretira kao podatak, a ne kao deo SQL naredbe.

Ovo smanjuje rizik od SQL injection napada prilikom prijavljivanja, registracije, pretrage i rada sa drugim podacima.
