import { populateDropdowns } from '../modules/utils.js';

export function initRennergebnisPage(){
    const citySelect = document.getElementById('citySelect');

    fetch('/get_cities')
        .then(response => response.json())
        .then(cities => {
            populateDropdowns([citySelect], cities, 'Stadt auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });

    citySelect.addEventListener('change', fillTabelle)
    // Trigger change event on page load to populate the table with the default city
    //citySelect.dispatchEvent(new Event('change'));


    function fillTabelle() {
        const tabelle = document.getElementById('rennergebnisTabelle').querySelector('tbody');
        const names = ['Alexander', 'Christine', 'Christoph', 'Jürgen', 'Simon'];

        const selectedCity = citySelect.value;

        fetch(`/get_punkte`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                city: selectedCity,
                names: names
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('API Antwort:', data);

            names.forEach((name, rowIndex) => {
                const tr = tabelle.rows[rowIndex];
                let td = tr.cells[1];

                if (data[name]) {
                    const punkte = data[name];
                    td.textContent = punkte;
                } else {
                    td.textContent = '0';
                }
            });
        })
        .catch(error => {
            console.error('Fehler:', error);
        });
    }


}