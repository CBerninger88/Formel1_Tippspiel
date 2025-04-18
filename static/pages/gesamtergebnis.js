export function initGesamtergebnisPage(){

    fillTabelle()

    function fillTabelle() {
        const tabelle = document.getElementById('gesamttabelle').querySelector('tbody');

        fetch('/get_gesamtpunkte', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => response.json())
        .then(data => {
            const { spieler, status } = data;

            spieler.forEach(([name, punkte], rowIndex) => {
                const tr = tabelle.rows[rowIndex];
                if (!tr) return;

                tr.cells[1].textContent = name ?? '';
                tr.cells[2].textContent = punkte ?? '';
            });
            if (!status.success) {
                alert(status.message);
            }
        })
        .catch(error => {
            console.error('Fehler:', error);
        });
    }


}

