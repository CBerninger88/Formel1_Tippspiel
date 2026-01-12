import { populateDropdowns } from '../modules/utils.js';

export function initSprintergebnisPage(){
    console.log('Admin Sprintergebnis-Seite Initialisierung');

    const citySelect = document.getElementById('city');
    const driverSelects = Array.from(document.querySelectorAll('[id^="driver"]'));
    const saveRennergebnisBtn = document.getElementById('rennergebnis');

    saveRennergebnisBtn.addEventListener('click', saveSelection);
    citySelect.addEventListener('change', fetchSprintergebnis);


    // 2. Dynamische Rennen-Dropdowns
    fetch('/admin/sprintergebnis_get_cities')
       .then(response => response.json())
       .then(cities => {
           populateDropdowns([citySelect], cities, 'Stadt auswählen');
       })
       .catch(error => {
           console.error('Fehler beim Laden der Städte:', error);
       });



    // 2. Dynamische Fahrer-Dropdowns
    fetch('/admin/rennergebnis_get_drivers')
        .then(response => response.json())
        .then(drivers => {
            populateDropdowns(driverSelects, drivers, 'Fahrer auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });


    function fetchSprintergebnis() {
        const selectedCity = citySelect.value;

        fetch(`/admin/get_sprintergebnis?city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                driverSelects.forEach((driverSelect, index) => {
                   const driverKey = `driver${index + 1}`;
                   driverSelect.value = data[driverKey] || "";
                });
                if (!data.success) {
                    alert(data.message);
                }

            });
    }


    function saveSelection() {
        const city = citySelect.value;
        const driverData = driverSelects.map(driver => driver.value);

        // Dictionary mit Keys (driver1, driver2, etc.) generieren
        const drivers = {};
        driverData.forEach((driver, index) => {
            drivers[`driver${index + 1}`] = driver;
        });

        fetch('/admin/save_sprintergebnis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({city, ...drivers}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }

}
