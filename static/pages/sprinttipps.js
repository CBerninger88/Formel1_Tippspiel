import { populateDropdowns } from '../modules/utils.js';

export function initSprinttippsPage(){
    console.log('Sprint-Tippabgabe- Seite Initialisierung');

    const citySelect = document.getElementById('city');
    const sdriverSelects = Array.from(document.querySelectorAll('[id^="sdriver"]'));
    const saveButton = document.getElementById('save');

    // 1. Dynamische Namen und Städte
    //const tippSpieler = ['Alexander', 'Christine', 'Christoph', 'Jürgen', 'Simon', 'Ergebnis'];
    //populateDropdowns([nameSelect], tippSpieler, 'Name auswählen');


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

    citySelect.addEventListener('change', fetchSelection);
    saveButton.addEventListener('click', saveSelection);
    [...sdriverSelects].forEach(select => {
        select.addEventListener('change', markAllDuplicates);
    });

    // Initiales Laden der gespeicherten Auswahl
    //citySelect.dispatchEvent(new Event('change'));

    // Event-Listener für das Ändern der Stadt oder Saison
    function fetchSelection() {
        const selectedCity = citySelect.value;

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id

        let selectionUrl = `/get_sprinttipps?city=${encodeURIComponent(selectedCity)}`;

        if (tipprunde_id) {
            selectionUrl += `&tipprunde_id=${tipprunde_id}`;
        }

        fetch(selectionUrl)
            .then(response => response.json())
            .then(data => {
                sdriverSelects.forEach((sDriverSelect, index) => {
                   const sDriverKey = `sdriver${index + 1}`;
                   sDriverSelect.value = data[sDriverKey] || "";
                });
                markAllDuplicates();
            });
    }

    // Event-Listener für den Klick auf den Speicher-Button
    function saveSelection() {
        const city = citySelect.value;
        const sDriverData = sdriverSelects.map(driver => driver.value);

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id;

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
            body: JSON.stringify({city, ...sDrivers, tipprunde_id: tipprunde_id ?? null}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }


    function markAllDuplicates() {
        markDuplicatesInGroup(sdriverSelects);   // Sprint
    }


    function markDuplicatesInGroup(selects) {
        const valueCount = {};

        selects.forEach(select => {
            const val = select.value;
            if (val) {
                valueCount[val] = (valueCount[val] || 0) + 1;
            }
        });

        selects.forEach(select => {
            const val = select.value;
            if (val && valueCount[val] > 1) {
                select.classList.add('driver-duplicate');
            } else {
                select.classList.remove('driver-duplicate');
            }
        });
    }
}