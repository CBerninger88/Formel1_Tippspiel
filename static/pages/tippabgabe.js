import { populateDropdowns } from '../modules/utils.js';

export function initTippabgabePage(){
    console.log('Tippabgabe- Seite Initialisierung');


    const nameSelect = document.getElementById('name');
    const citySelect = document.getElementById('city');
    const qdriverSelects = Array.from(document.querySelectorAll('[id^="qdriver"]'));
    const driverSelects = Array.from(document.querySelectorAll('[id^="driver"]'));
    const fDriverSelect = document.getElementById('fDriver');
    const saveButton = document.getElementById('save');

    // 1. Dynamische Namen und Städte
    const tippSpieler = ['Christine', 'Christoph', 'Jürgen'];
    populateDropdowns([nameSelect], tippSpieler, 'Name auswählen');

    const cities = [
    "Melbourne",
    "Shanghai",
    "Suzuka",
    "Sakhir",
    "Dschidda",
    "Miami",
    "Imola",
    "Monte Carlo",
    "Barcelona",
    "Montreal",
    "Spielberg",
    "Silverstone",
    "Spa-Francorchamps",
    "Budapest",
    "Zandvoort",
    "Monza",
    "Baku",
    "Singapur",
    "Austin",
    "Mexiko-Stadt",
    "São Paulo",
    "Las Vegas",
    "Doha",
    "Abu Dhabi"
];
    populateDropdowns([citySelect], cities, 'Stadt auswählen');

    // 2. Dynamische Fahrer-Dropdowns
    const fahrerListe = ["Max Verstappen", "Liam Lawson", "George Russell", "Paul Aron", "Charles Leclerc", "Lewis Hamilton", "Lando Norris", "Oscar Piastri", "Fernando Alonso", "Lance Stroll", "Pierre Gasly", "Jack Doohan", "Alexander Albon", "Logan Sargeant", "Isack Hadjar", "Franco Colapinto"];

    populateDropdowns(qdriverSelects, fahrerListe, 'Fahrer auswählen');
    populateDropdowns(driverSelects, fahrerListe, 'Fahrer auswählen');
    populateDropdowns([fDriverSelect], fahrerListe, 'Fahrer auswählen');

    nameSelect.addEventListener('change', fetchSelection);
    citySelect.addEventListener('change', fetchSelection);
    saveButton.addEventListener('click', saveSelection);

    // Initiales Laden der gespeicherten Auswahl
    //citySelect.dispatchEvent(new Event('change'));

    // Event-Listener für das Ändern der Stadt oder Saison
    function fetchSelection() {
        const selectedName = nameSelect.value;
        const selectedCity = citySelect.value;

        fetch(`/get_selection?name=${selectedName}&city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                qdriverSelects.forEach((qDriverSelect, index) => {
                   const qDriverKey = `qdriver${index + 1}`;
                   qDriverSelect.value = data[qDriverKey];// || "Fahrer";
                });
                driverSelects.forEach((driverSelect, index) => {
                   const driverKey = `driver${index + 1}`;
                   driverSelect.value = data[driverKey];// || "Fahrer";
                });

                fDriverSelect.value = data[`fdriver`];
            });
    }

    // Event-Listener für den Klick auf den Speicher-Button
    function saveSelection() {
        const name = nameSelect.value;
        const city = citySelect.value;
        const qDriverData = qdriverSelects.map(driver => driver.value);
        const driverData = driverSelects.map(driver => driver.value);

        // Dictionary mit Keys (driver1, driver2, etc.) generieren
        const qDrivers = {};
        qDriverData.forEach((driver, index) => {
            qDrivers[`qdriver${index + 1}`] = driver;
        });
        const drivers = {};
        driverData.forEach((driver, index) => {
            drivers[`driver${index + 1}`] = driver;
        });

        const fDriver = {};
        fDriver[`fDriver`] = fDriverSelect.value;

        fetch('/save_selection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, city, ...qDrivers, ...drivers, ...fDriver}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }
}