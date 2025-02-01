import { populateDropdowns } from '../modules/utils.js';

export function initwmStandPage(){
    console.log('WM Stand- Seite Initialisierung');

    const citySelect = document.getElementById('city');
    const wmdriverSelects = Array.from(document.querySelectorAll('[id^="wmdriver"]'));
    const getWMStandBtn = document.getElementById('getWMStand');

    getWMStandBtn.addEventListener('click', fetchSelection);

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

    function fetchSelection() {
        //const selectedCity = citySelect.value;

        fetch(`/get_wm_stand`)
            .then(response => response.json())
            .then(data => {
                wmdriverSelects.forEach((wmDriverSelect, index) => {
                   const wmDriverKey = `wmdriver${index + 1}`;
                   wmDriverSelect.value = data[wmDriverKey];// || "Fahrer";
                });
            });
    }

}
