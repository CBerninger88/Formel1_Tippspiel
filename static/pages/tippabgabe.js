import { populateDropdowns } from '../modules/utils.js';

export function initTippabgabePage(){
    console.log('Tippabgabe- Seite Initialisierung');


    const nameSelect = document.getElementById('name');
    const citySelect = document.getElementById('city');
    const qdriverSelects = Array.from(document.querySelectorAll('[id^="qdriver"]'));
    const driverSelects = Array.from(document.querySelectorAll('[id^="driver"]'));
    const fdriverSelect = document.getElementById('fdriver');
    const saveButton = document.getElementById('save');

    // 1. Dynamische Namen und Städte

    fetch('/get_users')
        .then(response => response.json())
        .then(names => {
            populateDropdowns([nameSelect], names, 'Name auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Namen:', error);
        });

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


    nameSelect.addEventListener('change', fetchSelection);
    citySelect.addEventListener('change', fetchSelection);
    saveButton.addEventListener('click', saveSelection);


    // Event-Listener für das Ändern der Stadt oder Saison
    function fetchSelection() {
        const selectedName = nameSelect.value;
        const selectedCity = citySelect.value;

        if (selectedName == 'Dummy_LR' || selectedName == 'Dummy_WM' || selectedName == 'Dummy_LY') {
            fetch(`/get_dummy?name=${selectedName}&city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                qdriverSelects.forEach((qDriverSelect, index) => {
                   qDriverSelect.disabled = false;
                   const qDriverKey = `qdriver${index + 1}`;
                   qDriverSelect.value = data[qDriverKey] || "";
                });
                driverSelects.forEach((driverSelect, index) => {
                   driverSelect.disabled = false;
                   const driverKey = `rdriver${index + 1}`;
                   driverSelect.value = data[driverKey] || "";
                });
                fdriverSelect.disabled = false;
                fdriverSelect.value = data[`fdriver`] || "";
            });
        } else {
            fetch(`/get_selection?name=${selectedName}&city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                qdriverSelects.forEach((qDriverSelect, index) => {
                   qDriverSelect.disabled = false;
                   const qDriverKey = `qdriver${index + 1}`;
                   qDriverSelect.value = data[qDriverKey] || "";
                   if (data['zeitschranke']) {
                        qDriverSelect.disabled = true;
                    }
                });
                driverSelects.forEach((driverSelect, index) => {
                   driverSelect.disabled = false;
                   const driverKey = `rdriver${index + 1}`;
                   driverSelect.value = data[driverKey] || "";
                   if (data['zeitschranke']) {
                        driverSelect.disabled = true;
                    }
                });

                fdriverSelect.value = data[`fdriver`] || "";
                fdriverSelect.disabled = false;
                if (data['zeitschranke']) {
                        fdriverSelect.disabled = true;
                    }
            });
        }

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
        fDriver[`fdriver`] = fdriverSelect.value;

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