import { populateDropdowns } from '../modules/utils.js';

export function initRennergebnisPage(){
    const citySelect = document.getElementById('citySelect');
    const calculateButton = document.getElementById('calculateButton');
    const nameSelect = document.getElementById('nameSelect')

    fetch('/get_cities')
        .then(response => response.json())
        .then(cities => {
            populateDropdowns([citySelect], cities, 'Stadt auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });

    citySelect.addEventListener('change', fillTabelle);
    citySelect.addEventListener('change', fetchDataAndPopulateTable);
    calculateButton.addEventListener('click', calculateNew);
    createTabelle();
    nameSelect.addEventListener('change', fetchDataAndPopulateTable);

    fetch('/get_users_rennergebnis')
        .then(response => response.json())
        .then(users => {
            populateDropdowns([nameSelect], users, 'Name auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der User:', error);
        });

    function fillTabelle() {
        fetchPunkte(false);
    }

    function calculateNew() {
        fetchPunkte(true);
    }

    function fetchPunkte(calcNew) {
        const tabelle = document.getElementById('rennergebnisTabelle').querySelector('tbody');
        const names = ['Alexander', 'Christine', 'Christoph', 'Jürgen', 'Klaus', 'Simon', 'Dummy_LR', 'Dummy_Kon', 'Dummy_LY', 'Dummy_WM'];

        const selectedCity = citySelect.value;

        fetch(`/get_punkte`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({city: selectedCity, calcNew})
        })
        .then(response => response.json())
        .then(data => {

            const {punkte, status} = data;

            if (Object.keys(punkte).length === 0) {
                alert(status.message);
                return; // Beende die Funktion, wenn keine Daten vorliegen
            }

            punkte.forEach((entry, rowIndex) => {
                const [name, details] = entry;
                const tr = tabelle.rows[rowIndex];

                if(!tr) return;

                const keys = ['qPunkte', 'rPunkte', 'fPunkte', 'gesamtPunkte'];
                tr.cells[1].textContent = name ?? '';
                for(let col = 2; col < tr.cells.length; col++) {
                    tr.cells[col].textContent = details[keys[col-2]] ?? '';
                }
            });
            //alert(status.message)
            if (!status.success) {
                alert(status.message);
            }
        })
        .catch(error => {
            console.error('Fehler:', error);
        });
    }

    function fetchDataAndPopulateTable(){
        const name = nameSelect.value;
        const selectedCity = citySelect.value;
        const tableWrapper = document.getElementById("tableWrapper2");

        if (!name) {
            tableWrapper.style.display = 'none';
            return;
        }

        tableWrapper.style.display = 'block';
        const tables = {
            'qtabelle': { keys: ['qpunkte', 'qdriver'], platzierungen: [1, 2, 3, 4] },
            'rtabelle': { keys: ['rpunkte', 'rdriver'], platzierungen: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] },
            'ftabelle': { keys: ['fpunkte', 'fdriver'], platzierungen: [''] }
        };

        fetch(`/get_einzeltipps?city=${selectedCity}&name=${name}`)
            .then(response => response.json())
            .then(data => {
                Object.entries(tables).forEach(([tableId, {keys, platzierungen}]) => {
                    const table = document.getElementById(tableId);
                    table.querySelector('thead').querySelectorAll('th')[1].textContent = name;

                    platzierungen.forEach((platz, rowIndex) => {
                        const row = table.querySelector('tbody').rows[rowIndex];

                        [name, 'Ergebnis', 'punkte'].forEach((entry, colIndex) => {
                            let key = keys[entry === 'punkte' ? 0 : 1] + platz;
                            row.cells[colIndex + 1].textContent = data[entry]?.[key] ?? '❓';
                        });
                    });
                });
            })
            .catch(error => console.error('Fehler:', error));
        }


    function createTabelle(){

        const container = document.querySelector(".container");
        const tableWrapper = document.createElement('div');
        tableWrapper.classList.add('table-wrapper');
        tableWrapper.id = 'tableWrapper2';
        tableWrapper.style.display = 'none';

        const tables = [
            { id: 'qtabelle', title: 'Qualifikation', rows: 4 },
            { id: 'rtabelle', title: 'Rennen', rows: 10 },
            { id: 'ftabelle', title: 'Schnellste Runde', rows: 1 }
        ];

        tables.forEach(({id, title, rows}) => {
            const table = document.createElement('table');
            table.id = id;

            table.innerHTML = `
                <thead>
                    <tr>
                        <th></th><th>Name</th><th>Ergebnis</th><th>Punkte</th>
                    </tr>
                </thead>
                <tbody>
                    ${Array.from({ length: rows }, (_, i) =>
                        `<tr><td>${i+1}</td><td></td><td></td><td></td></tr>`
                    ).join('')}
                </tbody>
            `;

            tableWrapper.appendChild(document.createElement('h1')).textContent = title;
            tableWrapper.appendChild(table);
        });
        container.appendChild(tableWrapper);

    }

}