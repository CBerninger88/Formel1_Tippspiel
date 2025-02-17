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

    function fetchDataAndPopulateTable(){
        const name = nameSelect.value;
        const selectedCity = citySelect.value;
        const tableWrapper = document.getElementById("tableWrapper2");
        const qtabelle = document.getElementById('qtabelle');
        const rtabelle = document.getElementById('rtabelle');
        const ftabelle = document.getElementById('ftabelle');

        const qplatzierungen = [1,2,3,4];
        const rplatzierungen = [1,2,3,4,5,6,7,8,9,10];

        if(name){
            qtabelle.querySelector('thead').querySelectorAll('th')[1].textContent = name;
            rtabelle.querySelector('thead').querySelectorAll('th')[1].textContent = name;
            ftabelle.querySelector('thead').querySelectorAll('th')[1].textContent = name;
            tableWrapper.style.display = 'block';
            const dataEntries = [name, 'Ergebnis', 'punkte'];

            fetch(`/get_einzeltipps?city=${selectedCity}&name=${name}`)
                .then(response => response.json())
                .then(data => {
                    dataEntries.forEach((entry, colIndex) => {
                        qplatzierungen.forEach((platz, rowIndex) => {
                            const tr = qtabelle.querySelector('tbody').rows[rowIndex];
                            let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                            if(!td) {
                                td = document.createElement('td');
                                tr.appendChild(td);
                            }

                            let qKey;
                            // Zugriff auf den jeweiligen Fahrer basierend auf der Platzierung
                            if (entry === 'punkte') {
                                qKey = `qpunkte${platz}`;
                            }else{
                                qKey = `qdriver${platz}`; // Schlüssel für den jeweiligen Fahrer
                            }

                            if (data[entry] && data[entry][qKey] != null) {
                                const punkte = data[entry][qKey];
                                td.textContent = punkte;

                            } else {
                                td.textContent = '❓';
                            }
                        });

                        // Race Ergebnisse eintragen
                        rplatzierungen.forEach((platz, rowIndex) => {
                            const tr = rtabelle.querySelector('tbody').rows[rowIndex];
                            let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                            if(!td) {
                                td = document.createElement('td');
                                tr.appendChild(td);
                            }

                            let rKey;
                            // Zugriff auf den jeweiligen Fahrer basierend auf der Platzierung
                            if (entry === 'punkte') {
                                rKey = `rpunkte${platz}`;
                            }else{
                                rKey = `rdriver${platz}`; // Schlüssel für den jeweiligen Fahrer
                            }

                            if (data[entry] && data[entry][rKey] != null) {
                                const punkte = data[entry][rKey];
                                td.textContent = punkte;

                            } else {
                                td.textContent = '❓';
                            }
                        });

                        // Punkte für Schnellste Runde eintragen
                        const tr = ftabelle.querySelector('tbody').rows[0];
                        let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                        if(!td) {
                            td = document.createElement('td');
                            tr.appendChild(td);
                        }

                        // Zugriff auf den jeweiligen Fahrer basierend auf der Platzierung
                        let fKey;
                        if (entry === 'punkte') {
                            fKey = `fpunkte`;
                        }else{
                            fKey = `fdriver`; // Schlüssel für den jeweiligen Fahrer
                        }
                        if (data[entry] && data[entry][fKey] != null) {
                            const punkte = data[entry][fKey];
                            td.textContent = punkte;
                        } else {
                            td.textContent = '❓';
                        }
                    })
                });

        } else {
                tableWrapper.style.display = 'none';

            }
    }

    function createTabelle(){

        // container im DOM finden
        const container = document.querySelector(".container");

        // table-wrapper erstellen
        const tableWrapper = document.createElement('div');
        tableWrapper.classList.add('table-wrapper');
        tableWrapper.style.display = 'none';
        tableWrapper.id = 'tableWrapper2'

        // h1 Element erstellen
        const qh1 = document.createElement('h1');
        qh1.textContent = 'Qualifikation';
        const rh1 = document.createElement('h1');
        rh1.textContent = 'Rennen';
        const fh1 = document.createElement('h1');
        fh1.textContent = 'Schnellste Runde';

        // Tabelle erstellen
        const qtabelle = document.createElement('table');
        const rtabelle = document.createElement('table');
        const ftabelle = document.createElement('table');
        qtabelle.id = 'qtabelle';
        rtabelle.id = 'rtabelle';
        ftabelle.id = 'ftabelle';

        // Header-Zeile erstellen
        const qthead = document.createElement('thead');
        const headerRow = document.createElement('tr');

        // Header Zeile befüllen
        name = nameSelect.value;
        const headers = ['', 'Name', 'Ergebnis', 'Punkte'];
        headers.forEach(text => {
            const th = document.createElement('th');
            th.textContent = text;
            headerRow.appendChild(th);
        });

        qthead.appendChild(headerRow);
        const rthead = qthead.cloneNode(true);
        const fthead = qthead.cloneNode(true);
        qtabelle.appendChild(qthead);
        rtabelle.appendChild(rthead);
        ftabelle.appendChild(fthead);

        // Tabellenkörper erstellen
        const tabellenListe = [qtabelle, rtabelle, ftabelle];
        const tabellenlaenge = [4, 10, 1];

        tabellenListe.forEach((tabelle, index) => {
            const tbody = document.createElement('tbody');

        // Füge ZEilen hinzu
        for (let i = 1; i <= tabellenlaenge[index]; i++) {
            const row = document.createElement('tr');

            const firstCell = document.createElement('td');
            firstCell.textContent = i;
            row.appendChild(firstCell);

            for(let j = 1; j < 4; j++) {
                const cell =  document.createElement('td');
                cell.textContent = '';
                row.appendChild(cell);
            }

            tbody.append(row);
            tabelle.appendChild(tbody);

        }


        });

        //qtabelle.appendChild(tbody);

        // TAbelle und h1 Elemente in das container Div Element einfügen
        tableWrapper.appendChild(qh1);
        tableWrapper.appendChild(qtabelle);
        tableWrapper.appendChild(rh1);
        tableWrapper.appendChild(rtabelle);
        tableWrapper.appendChild(fh1);
        tableWrapper.appendChild(ftabelle);
        container.appendChild(tableWrapper);

    }


}