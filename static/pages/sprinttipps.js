import { populateDropdowns } from '../modules/utils.js';

export function initSprinttippsPage(){
    console.log('Sprint-Tippabgabe- Seite Initialisierung');


    const nameSelect = document.getElementById('name');
    const citySelect = document.getElementById('city');
    const sdriverSelects = Array.from(document.querySelectorAll('[id^="sdriver"]'));
    const saveButton = document.getElementById('save');

    // 1. Dynamische Namen und Städte
    const tippSpieler = ['Christine', 'Christoph', 'Jürgen'];
    populateDropdowns([nameSelect], tippSpieler, 'Name auswählen');

    const cities = ['Melbourne', 'Schanghai', 'Suzuka', 'Bahrain'];
    populateDropdowns([citySelect], cities, 'Stadt auswählen');

    // 2. Dynamische Fahrer-Dropdowns
    const fahrerListe = ['Hamilton', 'Verstappen', 'Norris', 'Leclerc'];
    populateDropdowns(sdriverSelects, fahrerListe, 'Fahrer auswählen');

    nameSelect.addEventListener('change', fetchSelection);
    citySelect.addEventListener('change', fetchSelection);
    saveButton.addEventListener('click', saveSelection);

    // Initiales Laden der gespeicherten Auswahl
    //citySelect.dispatchEvent(new Event('change'));

    // Event-Listener für das Ändern der Stadt oder Saison
    function fetchSelection() {
        const selectedName = nameSelect.value;
        const selectedCity = citySelect.value;

        fetch(`/get_sprinttipps?name=${selectedName}&city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                sdriverSelects.forEach((sDriverSelect, index) => {
                   const sDriverKey = `sdriver${index + 1}`;
                   sDriverSelect.value = data[sDriverKey];// || "Fahrer";
                });
            });
    }

    // Event-Listener für den Klick auf den Speicher-Button
    function saveSelection() {
        const name = nameSelect.value;
        const city = citySelect.value;
        const sDriverData = sdriverSelects.map(driver => driver.value);

        // Dictionary mit Keys (driver1, driver2, etc.) generieren
        const sDrivers = {};
        sDriverData.forEach((driver, index) => {
            sDrivers[`sdriver${index + 1}`] = driver;
        });

        fetch('/save_sprinttipps', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, city, ...sDrivers}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }
}