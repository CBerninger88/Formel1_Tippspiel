import { populateDropdowns } from '../modules/utils.js';

export function initTippabgabePage(){
    console.log('Tippabgabe- Seite Initialisierung');


    const nameSelect = document.getElementById('name');
    const citySelect = document.getElementById('city');
    const driverSelects = Array.from(document.querySelectorAll('[id^="driver"]'));
    const saveButton = document.getElementById('save');

    // 1. Dynamische Namen und Städte
    const tippSpieler = ['Christine', 'Christoph', 'Jürgen'];
    populateDropdowns([nameSelect], tippSpieler, 'Name auswählen');

    const cities = ['Monza', 'Singapur', 'Austin'];
    populateDropdowns([citySelect], cities, 'Stadt auswählen');

    // 1. Dynamische Fahrer-Dropdowns
    const fahrerListe = ['Hamilton', 'Verstappen', 'Norris', 'Leclerc'];
    populateDropdowns(driverSelects, fahrerListe, 'Fahrer auswählen');


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
                driverSelects.forEach((qualiDriverSelect, index) => {
                   const qualiDriverKey = `driver${index + 1}`;
                   qualiDriverSelect.value = data[qualiDriverKey] || "Fahrer";
                });
            });
    }

    // Event-Listener für den Klick auf den Speicher-Button
    function saveSelection() {
        const name = nameSelect.value;
        const city = citySelect.value;
        const qualiDriverData = driverSelects.map(driver => driver.value);

        // Dictionary mit Keys (driver1, driver2, etc.) generieren
        const qualiDrivers = {};
        qualiDriverData.forEach((driver, index) => {
            qualiDrivers[`driver${index + 1}`] = driver;
        });

        fetch('/save_selection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, city, ...qualiDrivers}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }
}