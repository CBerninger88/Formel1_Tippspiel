import { populateDropdowns } from '../modules/utils.js';

export function initHomePage(){
    const citySelect = document.getElementById('citySelect');
    const downloadButton = document.getElementById('downloadButton');

    fetch('/get_cities')
        .then(response => response.json())
        .then(cities => {
            populateDropdowns([citySelect], cities, 'Stadt auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });

    citySelect.addEventListener('change', constructTabelle)
    downloadButton.addEventListener('click', downloadTabelle)
    // Trigger change event on page load to populate the table with the default city
    citySelect.dispatchEvent(new Event('change'));

    function downloadTabelle() {

        const table = ['qTippTabelle', 'rTippTabelle', 'fTippTabelle', 'stabelle'];
        const sheetNames = ['Qualifying', 'Rennen', 'Schnellste Runde', 'Sprint'];

        //Arbeitsmappe für Excel erstellen
        let wb = XLSX.utils.book_new();

        table.forEach((tableId, index) => {
            const table = document.getElementById(tableId);

            // Überprüfe, ob die Tabelle im DOM existiert
            if (!table) {
                console.log(`Tabelle mit der ID ${tableId} wurde nicht gefunden. Überspringe diese Tabelle.`);
                return;  // Überspringe die Tabelle, wenn sie nicht existiert
            }

            const rows = table.getElementsByTagName('tr');
            const tableData = [];

            // Tabellenkopf extrahieren
            const headers = rows[0].querySelectorAll('th');
            const headerArray = [];
            headers.forEach(header => {
                headerArray.push(header.innerText.trim());
            });
            tableData.push(headerArray); // Koopfzeile zu den Daten hinzufügen

            //Tabellendaten extrahieren
            for (let i = 1; i < rows.length; i++) {
                const cells = rows[i].querySelectorAll('td');
                const rowArray = [];
                cells.forEach(cell => {
                    rowArray.push(cell.innerText.trim());
                });
                tableData.push(rowArray); // Zeilen zu den Daten hinzufügen
            }

            // Daten in das Arbeitsblatt einfügen
            const ws = XLSX.utils.aoa_to_sheet(tableData);
            XLSX.utils.book_append_sheet(wb, ws, sheetNames[index]);
        });

        // Excel-Datei generieren und herunterladen
        XLSX.writeFile(wb, 'F1_Tippspiel.xlsx');
    }

    function constructTabelle() {
        const qTippTabelle = document.getElementById('qTippTabelle').querySelector('tbody');
        const rTippTabelle = document.getElementById('rTippTabelle').querySelector('tbody');
        const fTippTabelle = document.getElementById('fTippTabelle').querySelector('tbody');
        const names = ['Alexander','Christine', 'Christoph', 'Jürgen', 'Simon',  'Dummy_LY', 'Dummy_WM', 'Dummy_LR', 'Ergebnis'];
        const qplatzierungen = [1,2,3,4];
        const rplatzierungen = [1,2,3,4,5,6,7,8,9,10];
        qTippTabelle.innerHTML = '';
        rTippTabelle.innerHTML = '';
        fTippTabelle.innerHTML = '';

        // Initialisiere die Tabelle mit Platzierungen
        qplatzierungen.forEach(platz => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${platz}</td>`;
            qTippTabelle.appendChild(tr);
        });

        rplatzierungen.forEach(platz => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${platz}</td>`;
            rTippTabelle.appendChild(tr);
        });

        const tr = document.createElement('tr');
        tr.innerHTML = `<td> S</td>`;
        fTippTabelle.appendChild(tr);

        const selectedCity = citySelect.value;

        fetch(`/get_tipps?city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                console.log('API Antwort:', data);

                names.forEach((name, colIndex) => {
                    qplatzierungen.forEach((platz, rowIndex) => {
                        const tr = qTippTabelle.rows[rowIndex];
                        let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                        if(!td) {
                            td = document.createElement('td');
                            tr.appendChild(td);
                        }

                        // Zugriff auf den jeweiligen Fahrer basierend auf der Platzierung
                        const qdriverKey = `qdriver${platz}`; // Schlüssel für den jeweiligen Fahrer
                        if (data[name] && data[name][qdriverKey]) {
                            const driver = data[name][qdriverKey];
                            td.textContent = driver;
                        } else {
                            td.textContent = '❓';
                        }
                    });

                    rplatzierungen.forEach((platz, rowIndex) => {
                        const tr = rTippTabelle.rows[rowIndex];
                        let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                        if(!td) {
                            td = document.createElement('td');
                            tr.appendChild(td);
                        }

                        // Zugriff auf den jeweiligen Fahrer basierend auf der Platzierung
                        const rdriverKey = `rdriver${platz}`; // Schlüssel für den jeweiligen Fahrer
                        if (data[name] && data[name][rdriverKey]) {
                            const driver = data[name][rdriverKey];
                            td.textContent = driver;
                        } else {
                            td.textContent = '❓';
                        }
                    });

                    const tr = fTippTabelle.rows[0];
                    let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                    if(!td) {
                        td = document.createElement('td');
                        tr.appendChild(td);
                    }

                    // Zugriff auf den jeweiligen Fahrer basierend auf der Platzierung
                    const fdriverKey = `fdriver`; // Schlüssel für den jeweiligen Fahrer
                    if (data[name] && data[name][fdriverKey]) {
                        const driver = data[name][fdriverKey];
                        td.textContent = driver;
                    } else {
                        td.textContent = '❓';
                    }
                });

                const tableWrapper = document.querySelector(".table-wrapper");

                // h1 Element erstellen
                const sh1 = document.createElement('h1');
                sh1.id = 'sh1'
                sh1.textContent = 'Sprintrennen';
                sh1.style.display = 'none';

                if(data.sprint){

                    const h1 = document.getElementById("sh1");
                    if (h1) {
                        h1.remove();  // Entfernt das Element aus dem DOM
                    }

                    const table = document.getElementById("stabelle");
                    if (table) {
                        table.remove();  // Entfernt die gesamte Tabelle
                    }

                    // h1 Element erstellen
                    const sh1 = document.createElement('h1');
                    sh1.id = 'sh1'
                    sh1.textContent = 'Sprintrennen';
                    //sh1.style.display = 'block';

                    // Tabelle erstellen
                    const stabelle = document.createElement('table');
                    stabelle.id = 'stabelle';

                    // Header-Zeile erstellen
                    const sthead = document.createElement('thead');
                    const headerRow = document.createElement('tr');
                    // erste Spalte von Header
                    headerRow.appendChild(document.createElement('th'));

                    // Header Zeile befüllen
                    names.forEach((name, colIndex) => {
                        const th = document.createElement('th');
                        th.textContent = name;
                        headerRow.appendChild(th);
                    });

                    sthead.appendChild(headerRow);
                    stabelle.appendChild(sthead);

                    const tbody = document.createElement('tbody');

                    for (let platz = 1; platz <= 8; platz++) {
                        const row = document.createElement('tr');

                        const firstCell = document.createElement('td');
                        firstCell.textContent = platz;
                        row.appendChild(firstCell);

                        names.forEach((name, idx) => {
                            const cell =  document.createElement('td');
                            //Zugriff auf den jeweiligen Fahrer basierend auf der Platzierung
                            const sdriverKey = `sdriver${platz}`; // Schlüssel für den jeweiligen Fahrer
                            if (data[name] && data[name][sdriverKey]) {
                                const driver = data[name][sdriverKey];
                                cell.textContent = driver;
                            } else {
                                cell.textContent = '❓';
                            }
                            row.appendChild(cell);

                        });

                        tbody.append(row);
                        stabelle.appendChild(tbody);

                    }

                    tableWrapper.appendChild(sh1);
                    tableWrapper.appendChild(stabelle);
                    //container.appendChild(tableWrapper);

                } else {
                    const sh1 = document.getElementById("sh1");
                    if (sh1) {
                        sh1.remove();  // Entfernt das Element aus dem DOM
                    }

                    const table = document.getElementById("stabelle");
                    if (table) {
                        table.remove();  // Entfernt die gesamte Tabelle
                    }
                }


            });
    }
}