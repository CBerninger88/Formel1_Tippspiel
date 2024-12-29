export function initHomePage(){
    const citySelect = document.getElementById('citySelect');
    const downloadButton = document.getElementById('downloadButton');

    citySelect.addEventListener('change', constructTabelle)
    downloadButton.addEventListener('click', downloadTabelle)
    // Trigger change event on page load to populate the table with the default city
    citySelect.dispatchEvent(new Event('change'));

    function downloadTabelle() {
        // Rufe die Tabelle ab
        const table = document.getElementById('tippTabelle');
        const rows = table.querySelectorAll('tr');
        const data = [];

        // Gehe durch die Zeilen der Tabelle
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            const rowData = [];

            // Gehe durch die Zellen und extrahiere den Textinhalt
            cells.forEach(cell => {
                rowData.push(cell.textContent);
            });

            // Füge die Daten der Zeile zur CSV hinzu
            data.push(rowData);
        });

        // Erstelle ein Arbeitsblatt (worksheet) aus den extrahierten Daten
        const ws = XLSX.utils.aoa_to_sheet(data);

        // Erstelle eine Arbeitsmappe (workbook) und füge das Arbeitsblatt hinzu
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Tabelle");

        // Erstelle den Download-Link und löse den Download aus
        XLSX.writeFile(wb, "tabelle.xlsx"); // Datei wird mit dem Namen "tabelle.xlsx" heruntergeladen
    }

    function constructTabelle() {
        const tippTabelle = document.getElementById('tippTabelle').querySelector('tbody');
        const names = ['Christine', 'Christoph', 'Jürgen'];
        const platzierungen = [1,2,3]
        tippTabelle.innerHTML = '';

        // Initialisiere die Tabelle mit Platzierungen
        platzierungen.forEach(platz => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${platz}</td>`;
            tippTabelle.appendChild(tr);
        });

        const selectedCity = citySelect.value
        fetch(`/get_tipps?city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                console.log('API Antwort:', data);

                names.forEach((name, colIndex) => {
                    platzierungen.forEach((platz, rowIndex) => {
                        const tr = tippTabelle.rows[rowIndex];
                        let td = tr.cells[colIndex + 1]; //+1 wegen der PLatzierungsspalte

                        if(!td) {
                            td = document.createElement('td');
                            tr.appendChild(td);
                        }

                        if (data[name] && data[name][0][platz -1]) {
                            const driver = data[name][0][platz - 1];
                            td.textContent = `${driver}`;
                        } else {
                            td.textContent = 'N/A';
                        }
                    });
                });
            });
    }
}