// document, najbitniji
const forma = document.getElementById("formaprijava")

forma.addEventListener("submit", function(event){
    event.preventDefault();
    const tim = document.getElementById("tim").value;
    const kategorija = document.getElementById("kategorija").value;
    const kontakt = document.getElementById("kontakt").value;
    const email = document.getElementById("mail").value;
    const brojigraca = document.getElementById("broj").value;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email)) {
        alert("Unesite ispravnu e-mail adresu.");
        return;
    }

    // broj igraca treba da bude od 1 do 15, 
    // ako je manje od 1 alert, ako je vise od 15 alert
    if(brojigraca < 1){
        alert("Broj igraca mora da bude veci od 0")
        return;
    }
    if (brojigraca > 15){
        alert("Broj igraca mora da bude manji od 15")
        return;
    }

    if (kategorija == "juniori"){
        alert("izabrali ste juniore");
    }

    const kotizacija = brojigraca * 50;

    const element = document.createElement("li");
    element.innerHTML = "tim: " +  tim + " br ig: " + brojigraca + " kotizacija: " + kotizacija
    
    main = document.getElementById("listaPrijava")

    main.appendChild(element)
    forma.reset();
})