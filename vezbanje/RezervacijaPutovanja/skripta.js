const form = document.getElementById("reservationForm");

form.addEventListener("submit", function(event) {

    event.preventDefault();

    const ime = document.getElementById("ime").value;
    const email = document.getElementById("email").value;
    const destinacija = document.getElementById("destinacija").value;
    const putnici = document.getElementById("putnici").value;

    // Provera e-mail adrese
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email)) {
        alert("Unesite ispravnu e-mail adresu.");
        return;
    }

    // Provera broja putnika
    if (putnici <= 0) {
        alert("Broj putnika mora biti pozitivan.");
        return;
    }

    // Izračunavanje cene
    const cena = putnici * 100;

    // Kreiranje stavke rezervacije
    const stavka = document.createElement("li");

    stavka.textContent =
        ime + " - " + destinacija + " - Cena: " + cena + " EUR";

    // Dodavanje stavke u listu
    document.getElementById("reservationList").appendChild(stavka);

    form.reset();
});