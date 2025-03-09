import { populateDropdowns } from '../modules/utils.js';

export function initSprinttippsPage(){
    console.log('Sprint-Tippabgabe- Seite Initialisierung');


    const nameSelect = document.getElementById('name');
    const citySelect = document.getElementById('city');
    const sdriverSelects = Array.from(document.querySelectorAll('[id^="sdriver"]'));
    const saveButton = document.getElementById('save');

    // 1. Dynamische Namen und Städte
    //const tippSpieler = ['Alexander', 'Christine', 'Christoph', 'Jürgen', 'Simon', 'Ergebnis'];
    //populateDropdowns([nameSelect], tippSpieler, 'Name auswählen');

    fetch('/get_users')
        .then(response => response.json())
        .then(names => {
            populateDropdowns([nameSelect], names, 'Name auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Namen:', error);
        });

    fetch('/sprint_get_cities')
        .then(response => response.json())
        .then(cities => {
            populateDropdowns([citySelect], cities, 'Stadt auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });

    // 2. Dynamische Fahrer-Dropdowns
    fetch('/get_drivers')
        .then(response => response.json())
        .then(drivers => {
            populateDropdowns(sdriverSelects, drivers, 'Fahrer auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });

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
                   sDriverSelect.value = data[sDriverKey] || "";
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