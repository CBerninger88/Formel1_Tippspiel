import { populateDropdowns } from '../modules/utils.js';

export function initTippabgabePage(){
    console.log('Tippabgabe- Seite Initialisierung');

    const FIRST_RACE_CITY = 'Melbourne, 2026-03-08';
    const copyLastTipBtn = document.getElementById('copy-last-tip');
    const citySelect = document.getElementById('city');
    const qdriverSelects = Array.from(document.querySelectorAll('[id^="qdriver"]'));
    const driverSelects = Array.from(document.querySelectorAll('[id^="driver"]'));
    const fdriverSelect = document.getElementById('fdriver');
    const saveButton = document.getElementById('save');

    fetch('/races_get_cities')
        .then(response => response.json())
        .then(cities => {
            populateDropdowns([citySelect], cities, 'Stadt auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });
    // populateDropdowns([citySelect], cities, 'Stadt auswählen');

    // 2. Dynamische Fahrer-Dropdowns
    fetch('/get_drivers')
        .then(response => response.json())
        .then(drivers => {
            populateDropdowns(qdriverSelects, drivers, 'Fahrer auswählen');
            populateDropdowns(driverSelects, drivers, 'Fahrer auswählen');
            populateDropdowns([fdriverSelect], drivers, 'Fahrer auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });


    //nameSelect.addEventListener('change', fetchSelection);
    citySelect.addEventListener('change', fetchSelection);
    saveButton.addEventListener('click', saveSelection);
    [...qdriverSelects, ...driverSelects].forEach(select => {
        select.addEventListener('change', markAllDuplicates);
    });
    copyLastTipBtn.addEventListener('click', () => {
        if (!confirm('Aktuelle Auswahl überschreiben?')) {
            return; //
        }
        fetchSelection({ usePrevious: true });
    });



    // Event-Listener für das Ändern der Stadt oder Saison
     function fetchSelection({ usePrevious = false } = {}) {
        const selectedCity = citySelect.value;

        const copyBtn = document.getElementById('copy-last-tip');

        // 🔴 Melbourne = erstes Rennen → Button aus
    if (!selectedCity || selectedCity === FIRST_RACE_CITY) {
        copyBtn.disabled = true;
    } else {
        // 3-Tage-Regel prüfen
        const parts = selectedCity.split(', ');
        if (parts.length < 2) {
            copyBtn.disabled = true;
        } else {
            const renndatumStr = parts[1]; // "yyyy-mm-dd"
            const renndatum = new Date(renndatumStr);
            const heute = new Date();

            const diffTime = renndatum - heute; // Millisekunden
            const diffDays = diffTime / (1000 * 60 * 60 * 24);

            // Button nur aktivieren, wenn mindestens 3 Tage vor dem Rennen
            copyBtn.disabled = diffDays < 3;
        }
    }

        if (!selectedCity) {
            alert('Bitte zuerst ein Rennen auswählen');
            return;
        }

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id;

        let selectionUrl = usePrevious
            ? `/get_last_selection?city=${encodeURIComponent(selectedCity)}`
            : `/get_selection?city=${encodeURIComponent(selectedCity)}`;

        if (tipprunde_id) {
            selectionUrl += `&tipprunde_id=${tipprunde_id}`;
        }

        fetch(selectionUrl)
            .then(response => response.json())
            .then(data => {
                if (!data || Object.keys(data).length === 0) {
                    alert('Kein Tipp gefunden.');
                    return;
                }

                // Qualifikation
                qdriverSelects.forEach((qDriverSelect, index) => {
                    qDriverSelect.disabled = false;
                    qDriverSelect.value = data[`qdriver${index + 1}`] || "";
                    if (data.zeitschranke) qDriverSelect.disabled = true;
                });

                // Rennen
                driverSelects.forEach((driverSelect, index) => {
                    driverSelect.disabled = false;
                    driverSelect.value = data[`rdriver${index + 1}`] || "";
                    if (data.zeitschranke) driverSelect.disabled = true;
                });

                // Schnellste Runde
                fdriverSelect.disabled = false;
                fdriverSelect.value = data.fdriver1 || "";
                if (data.zeitschranke) fdriverSelect.disabled = true;

                markAllDuplicates();
            });
    }

    // Event-Listener für den Klick auf den Speicher-Button
    function saveSelection() {
        const city = citySelect.value;
        const qDriverData = qdriverSelects.map(driver => driver.value);
        const driverData = driverSelects.map(driver => driver.value);

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id;

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
        fDriver[`fdriver`] = fdriverSelect.value;

        fetch('/save_selection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({city, ...qDrivers, ...drivers, ...fDriver, tipprunde_id: tipprunde_id ?? null}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }



    function markAllDuplicates() {
        markDuplicatesInGroup(qdriverSelects);   // Quali
        markDuplicatesInGroup(driverSelects);    // Rennen
        // fdriver absichtlich NICHT prüfen
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