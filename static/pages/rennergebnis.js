import { populateDropdowns } from '../modules/utils.js';

export function initRennergebnisPage(){
    const citySelect = document.getElementById('citySelect');
    const calculateButton = document.getElementById('calculateButton');

    fetch('/get_cities')
        .then(response => response.json())
        .then(cities => {
            populateDropdowns([citySelect], cities, 'Stadt auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });

    citySelect.addEventListener('change', fillTabelle)
    calculateButton.addEventListener('click', calculateNew)
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
                city: selectedCity
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('API Antwort:', data);

            names.forEach((name, rowIndex) => {
                const tr = tabelle.rows[rowIndex];
                const columnCount = tr.cells.length;
                const keys = ['qPunkte', 'rPunkte', 'fPunkte', 'gesamtPunkte'];
                let td = tr.cells[1];

                if (data[name]) {
                    for (let col = 1; col < columnCount; col++) {
                        tr.cells[col].textContent = data[name][keys[col-1]];
                    }
                    //const columnCount = table.rows[0].cells.length;
                    //tr.cells.forEach(test => {
                        //const cell = row.insertCell();   // Neue Zelle hinzufügen
                   //     test.textContent = data[name]['gesamtPunkte'];     // Inhalt setzen
                    //});
                    //const punkte = data[name]['gesamtPunkte'];
                    //td.textContent = punkte;
                } else {
                    for (let col = 1; col < columnCount; col++) {
                        tr.cells[col].textContent = 0;
                    }
                }
            });
            if (!data.success) {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Fehler:', error);
        });
    }

    function calculateNew(){
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
                calcNew: true
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('API Antwort:', data);

            names.forEach((name, rowIndex) => {
                const tr = tabelle.rows[rowIndex];
                const columnCount = tr.cells.length;
                const keys = ['qPunkte', 'rPunkte', 'fPunkte', 'gesamtPunkte'];
                let td = tr.cells[1];

                if (data[name]) {
                    for (let col = 1; col < columnCount; col++) {
                        tr.cells[col].textContent = data[name][keys[col-1]];
                    }
                } else {
                    for (let col = 1; col < columnCount; col++) {
                        tr.cells[col].textContent = 0;
                    }
                }
            });
            if (!data.success) {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Fehler:', error);
        });

    }


}