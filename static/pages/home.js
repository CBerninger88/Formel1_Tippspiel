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
    // downloadButton.addEventListener('click', downloadTabelle)
    // Trigger change event on page load to populate the table with the default city
    citySelect.dispatchEvent(new Event('change'));

    function downloadTabelle() {
        const city = citySelect.value ? citySelect.value.split(', ')[0] : 'Unbekannt';
        const table = ['qTippTabelle', 'rTippTabelle', 'fTippTabelle', 'stabelle'];
        const sheetNames = [`Qualifying (${city})`, `Rennen (${city})`, `Schnellste Runde (${city})`, `Sprint (${city})`];

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
        const safeCity = city.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, '_');
        XLSX.writeFile(wb, `F1_Tippspiel_${safeCity}.xlsx`);
    }

    function constructTabelle() {
        const qTippTabelle = document.getElementById('qTippTabelle')?.querySelector('tbody');
        const rTippTabelle = document.getElementById('rTippTabelle')?.querySelector('tbody');
        const fTippTabelle = document.getElementById('fTippTabelle')?.querySelector('tbody');

        if (!qTippTabelle || !rTippTabelle || ! fTippTabelle) return

        const selectedCity = document.getElementById('citySelect').value;

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id;

        let usersUrl = '/get_users';
        let tippsUrl = `/get_tipps?city=${encodeURIComponent(selectedCity)}`;

        if (tipprunde_id) {
            usersUrl += `?tipprunde_id=${tipprunde_id}`;
            tippsUrl += `&tipprunde_id=${tipprunde_id}`;
        }

        //const names = ['Alexander','Christine', 'Christoph', 'Jürgen', 'Klaus', 'Simon',  'Dummy_LY', 'Dummy_Kon', 'Dummy_WM', 'Dummy_LR', 'Ergebnis'];
        const qplatzierungen = [1,2,3,4];
        const rplatzierungen = [1,2,3,4,5,6,7,8,9,10];

        qTippTabelle.innerHTML = '';
        rTippTabelle.innerHTML = '';
        fTippTabelle.innerHTML = '';


        // Initialisiere die Tabelle mit Platzierungen
        qplatzierungen.forEach(platz => {
            qTippTabelle.innerHTML += `<tr><td>${platz}</td></tr>`;
        });

        rplatzierungen.forEach(platz => {
            rTippTabelle.innerHTML += `<tr><td>${platz}</td></tr>`;
        });

        fTippTabelle.innerHTML += `<tr><td> S</td></tr>`;


        // 1️⃣ Usernamen der Tipprunde laden
        fetch(usersUrl)
            .then(res => res.json())
            .then(names => {
                if (!names.length) return;

                // 2️⃣ Tipps für die Tabellen laden
            fetch(tippsUrl)
                .then(response => {
                    if(!response.ok) {
                        throw new Error(`Fehlerhafte Antwort: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('API Antwort:', data);

                    names.forEach((name, colIndex) => {
                        qplatzierungen.forEach((platz, rowIndex) => {
                            const tr = qTippTabelle.rows[rowIndex];
                            if (!tr) return;

                            let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte
                            if(!td) {
                                td = document.createElement('td');
                                tr.appendChild(td);
                            }

                            td.textContent = data[name]?.[`qdriver${platz}`] || '❓';

                        });

                        rplatzierungen.forEach((platz, rowIndex) => {
                            const tr = rTippTabelle.rows[rowIndex];
                            if (!tr) return;

                            let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte
                            if(!td) {
                                td = document.createElement('td');
                                tr.appendChild(td);
                            }

                            td.textContent = data[name]?.[`rdriver${platz}`] || '❓';
                        });

                        const tr = fTippTabelle.rows[0];
                        let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                        if(!td) {
                            td = document.createElement('td');
                            tr.appendChild(td);
                        }

                        td.textContent = data[name]?.[`fdriver1`] || '❓';
                    });

                    const tableWrapper = document.querySelector(".table-wrapper");
                    document.getElementById("sh1")?.remove();
                    document.getElementById("stabelle")?.remove();

                    if (data.sprint) {
                        const sh1 = document.createElement('h1');
                        sh1.id = 'sh1';
                        sh1.textContent = 'Sprintrennen';

                        const stabelle = document.createElement('table');
                        stabelle.id = 'stabelle';

                        const sthead = document.createElement('thead');
                        const headerRow = document.createElement('tr');

                        headerRow.appendChild(document.createElement('th'));
                        names.forEach(name => {
                            const th = document.createElement('th');
                            th.textContent = name;
                            headerRow.appendChild(th);
                        });

                        sthead.appendChild(headerRow);
                        stabelle.appendChild(sthead);

                        const tbody = document.createElement('tbody');

                        for (let platz = 1; platz <= 8; platz++) {
                            const row = document.createElement('tr');
                            row.innerHTML = `<td>${platz}</td>` + names.map(name =>
                                `<td>${data[name]?.[`sdriver${platz}`] || '❓'}</td>`).join('');
                            tbody.appendChild(row);
                        }

                        stabelle.appendChild(tbody);
                        tableWrapper.appendChild(sh1);
                        tableWrapper.appendChild(stabelle);
                    }

                })
                .catch(error => console.error('Fehler beim Laden der Tipps:', error));
            })
        .catch(err => console.error("Fehler beim Laden der User:", err));

    }
}