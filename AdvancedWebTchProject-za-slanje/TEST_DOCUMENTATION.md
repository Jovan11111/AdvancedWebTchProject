# Dokumentacija testiranja

## 1. Svrha

Ovaj dokument opisuje automatizovane API testove i snimljene frontend scenarije za aplikaciju Online biblioteka.

Testovi pokrivaju prijavljivanje, upravljanje korisnicima, knjige, statuse čitanja, prijatelje, administraciju i osnovnu navigaciju kroz aplikaciju.

## 2. Obuhvat testiranja

### Backend API

Backend testovi su implementirani pomoću alata `pytest` u fajlu `backend/tests/test_api.py`.

| Oblast | Pokriveni scenariji |
|---|---|
| Provera dostupnosti i knjige | Provera zdravlja sistema i početni katalog knjiga |
| Registracija | Uspešna registracija, obavezna polja, dupli username/email |
| Prijavljivanje | Uspešno prijavljivanje, nepostojeći username, neispravna lozinka |
| Lozinke | Pravila jačine lozinke i validacija promene lozinke |
| Detalji knjige | Postojeća i nepostojeća knjiga |
| Status čitanja | Prijavljivanje, nepostojeća knjiga, neispravan status, uspešna izmena |
| Prijatelji | Dodavanje, dupli prijatelj, nepostojeći korisnik, lista, aktivnosti, uklanjanje |
| Administracija | Dozvole za knjige, dodavanje/brisanje knjige, dupli ISBN, prevelika slika |
| Korisnici | Lista korisnika, brisanje korisnika, zaštita administratorskog naloga |
| Statički fajlovi | Endpoint za početnu naslovnicu knjige |

### Frontend

Snimljeni scenariji za browser nalaze se u fajlu `frontend/Online biblioteka testovi.krecorder` i namenjeni su pokretanju pomoću alata Katalon Recorder/Selenium IDE.

| Scenario | Očekivani rezultat |
|---|---|
| Uspešno prijavljivanje | Ispravni administratorski podaci vode korisnika u biblioteku |
| Neuspešno prijavljivanje | Neispravni podaci prikazuju grešku pri prijavljivanju |
| Uspešna registracija | Kreira se novi korisnički nalog |
| Neuspešna registracija | Neispravni podaci za registraciju se odbijaju |
| Pretraga knjiga | Rezultati pretrage se menjaju prema unetom naslovu ili upitu |
| Status čitanja | Knjiga se označava kao pročitana, željena ili nepročitana |
| Dodavanje i uklanjanje prijatelja | Korisnik se dodaje na listu prijatelja i može da se ukloni |
| Administracija | Administrator može da doda/obriše knjige i obriše običnog korisnika |

## 3. Test okruženje

- Backend: Flask API
- Frontend: Angular aplikacija
- Baza podataka: SQLite
- Osnovni URL API-ja: `http://localhost:5000`
- URL frontenda: `http://localhost:4200`
- Testna backend baza: privremena SQLite baza koju kreira pytest
- Browser testovi: Chrome-kompatibilan browser sa recorder ekstenzijom

Podrazumevani administratorski nalog koji koriste snimljeni testovi:

```text
Username: admin
Lozinka: admin123
```

## 4. Preduslovi

1. Docker Desktop je pokrenut ili su backend i frontend pokrenuti lokalno.
2. Backend je dostupan na adresi `http://localhost:5000`.
3. Frontend je dostupan na adresi `http://localhost:4200`.
4. Baza sadrži podrazumevani administratorski nalog i početne knjige.
5. Snimljeni testovi se izvršavaju nad čistom ili kontrolisanom testnom bazom sa potrebnim korisnicima i knjigama.

Pokretanje cele aplikacije pomoću Dockera:

```powershell
docker compose up --build
```

## 5. Pokretanje backend testova

Iz root foldera projekta, pomoću backend virtuelnog okruženja:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend\tests\test_api.py -q
```

Backend skup sadrži 11 testova. Uspešno izvršavanje prikazuje da su svi testovi prošli.

## 6. Pokretanje frontend testova

1. Pokreni aplikaciju:

```powershell
docker compose up
```

2. Otvori recorder ekstenziju u podržanom browseru.
3. Otvori snimljeni projekat iz fajla:

```text
frontend/Online biblioteka testovi.krecorder
```

4. Pokreni svaki scenario pojedinačno i proveri očekivani rezultat.

## 7. Očekivani rezultati

- API endpointi vraćaju navedene statusne kodove za uspeh ili validaciju.
- Neispravan unos prikazuje razumljivu poruku o grešci.
- Uspešno prijavljivanje preusmerava korisnika na katalog knjiga.
- Izmene statusa čitanja ostaju vidljive na korisničkom profilu.
- Dodati prijatelji se pojavljuju na listi i mogu da se uklone.
- Samo administratori mogu da upravljaju knjigama i korisnicima.
- Obrisani zapisi se više ne pojavljuju na odgovarajućoj listi.

## 8. Napomene i ograničenja

- Snimljeni frontend scenariji koriste unapred definisane username vrednosti, lozinke, naslove knjiga i URL-ove; pri ponovljenom pokretanju može biti potrebno čišćenje baze ili ažuriranje podataka.
- Browser recorder zavisi od aktivnog browsera i verzije ekstenzije. Stabilni ID selektori kao što su `login-username`, `login-password`, `friend-username` i `reading-status` treba da imaju prednost nad pozicionim XPath selektorima.
- Backend testovi koriste izolovanu privremenu bazu i nezavisni su od razvojne baze.
