import { populateDropdowns } from '../modules/utils.js';

export function initwmStandPage(){
    console.log('WM Stand- Seite Initialisierung');


        const wmStandTabelle = document.getElementById('wmStandTabelle')?.querySelector('tbody');
        const konstrukteursTabelle = document.getElementById('konstrukteursTabelle')?.querySelector('tbody');

        if (!wmStandTabelle || !konstrukteursTabelle) return

        const fahrerplatzierungen = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
        const teamplatzierungen = [1,2,3,4,5,6,7,8,9,10];
        wmStandTabelle.innerHTML = '';

        // Initialisiere die Tabelle mit Platzierungen
        //fahrerplatzierungen.forEach(platz => {
        //    wmStandTabelle.innerHTML += `<tr><td>${platz}.</td></tr>`;
        //});
        teamplatzierungen.forEach(platz => {
            konstrukteursTabelle.innerHTML += `<tr><td>${platz}.</td></tr>`;
        });

        const rennenCity = document.getElementById('rennenLabel').dataset.rennenCity;

        fetch(`/get_wm_stand?rennen=${encodeURIComponent(rennenCity)}`)
            .then(response => {
                    if(!response.ok) {
                        throw new Error(`Fehlerhafte Antwort: ${response.status}`);
                    }
                    return response.json();
            })
            .then(data => {
                console.log('API Antwort:', data);

                if (!data.success) {
                    alert(data.message || 'Fehler beim Laden des WM-Stands');
                    return;
                }

                // Tabelle leeren
                wmStandTabelle.innerHTML = '';

                data.wm_stand.forEach(row => {
                    const tr = document.createElement('tr');

                    tr.innerHTML = `
                        <td>${row.platz}</td>
                        <td>${row.driver ?? '❓'}</td>
                        <td>${row.punkte ?? '❓'}</td>
                    `;

                    wmStandTabelle.appendChild(tr);
                });
            })
            .catch(error => console.error('Fehler beim Laden der Tipps:', error));


        fetch(`/get_team_stand?rennen=${encodeURIComponent(rennenCity)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Fehlerhafte Antwort: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('API Antwort:', data);

                if (!data.success) {
                    alert(data.message || 'Fehler beim Laden der Teamwertung');
                    return;
                }

                const tbody = document
                    .getElementById('konstrukteursTabelle')
                    .querySelector('tbody');

                tbody.innerHTML = '';

                data.team_wm.forEach(row => {
                    const tr = document.createElement('tr');

                    tr.innerHTML = `
                        <td>${row.platz}</td>
                        <td>${row.team}</td>
                        <td>${row.punkte ?? 0}</td>
                    `;

                    tbody.appendChild(tr);
                });
            })
            .catch(error => console.error('Fehler beim Laden der Teamwertung:', error));


}
