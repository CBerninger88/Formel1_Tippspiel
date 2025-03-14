import { populateDropdowns } from '../modules/utils.js';

export function initwmStandPage(){
    console.log('WM Stand- Seite Initialisierung');

    const citySelect = document.getElementById('city');
    const wmdriverSelects = Array.from(document.querySelectorAll('[id^="wmdriver"]'));
    const saveWMStandBtn = document.getElementById('wmStand');

    saveWMStandBtn.addEventListener('click', saveSelection);
    citySelect.addEventListener('change', fetchWMStand);


    // 2. Dynamische Rennen-Dropdowns
    fetch('/wmStand_get_cities')
       .then(response => response.json())
       .then(cities => {
           populateDropdowns([citySelect], cities, 'Stadt auswählen');
       })
       .catch(error => {
           console.error('Fehler beim Laden der Städte:', error);
       });



    // 2. Dynamische Fahrer-Dropdowns
    fetch('/wmStand_get_drivers')
        .then(response => response.json())
        .then(drivers => {
            populateDropdowns(wmdriverSelects, drivers, 'Fahrer auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });


    function fetchWMStand() {
        const selectedCity = citySelect.value;

        fetch(`/get_wm_stand?city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                wmdriverSelects.forEach((wmDriverSelect, index) => {
                   const wmDriverKey = `wmdriver${index + 1}`;
                   wmDriverSelect.value = data[wmDriverKey] || "";
                });
                if (!data.success) {
                    alert(data.message);
                }
            });
    }


    function saveSelection() {
        const city = citySelect.value;
        const wmDriverData = wmdriverSelects.map(driver => driver.value);

        // Dictionary mit Keys (driver1, driver2, etc.) generieren
        const wmDrivers = {};
        wmDriverData.forEach((driver, index) => {
            wmDrivers[`wmdriver${index + 1}`] = driver;
        });

        fetch('/save_wm_stand', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({city, ...wmDrivers}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }

}
