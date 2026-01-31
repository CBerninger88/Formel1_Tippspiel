import { populateDropdowns } from '../modules/utils.js';

export function initGesamtergebnisPage(){

    const citySelect = document.getElementById('citySelect');

    fetch('/races_get_cities')
        .then(response => response.json())
        .then(cities => {
            populateDropdowns([citySelect], cities, 'Stadt auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Städte:', error);
        });

    citySelect.addEventListener('change', () => {
        fetchPunkte(false);
    });

    fillTabelle()

    function fillTabelle() {
        const tbody = document.getElementById('gesamttabelle').querySelector('tbody');

        tbody.innerHTML = ''; // 🔥 Reset

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id;

        fetch(`/get_gesamtpunkte?tipprunde_id=${tipprunde_id}`)
            .then(res => res.json())
            .then(data => {
                data.players.forEach((player, index) => {
                    const tr = document.createElement('tr');

                    tr.innerHTML = `
                        <td>${index + 1}.</td>
                        <td>${player.username}</td>
                        <td>${player.points}</td>
                    `;

                    tbody.appendChild(tr);
                });
            })
            .catch(err => console.error(err));
    }

    function fetchPunkte() {
        const tbody = document.getElementById('rennergebnisTabelle').querySelector('tbody');

        tbody.innerHTML = '';

        const selectedCity = citySelect.value;

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id;

        fetch(`/get_racepunkte?city=${encodeURIComponent(selectedCity)}&tipprunde_id=${tipprunde_id}`)
            .then(res => res.json())
            .then(data => {
                data.players.forEach((player, index) => {
                    const p = player.points;

                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${index + 1}.</td>
                        <td>${player.username}</td>
                        <td>${p.quali}</td>
                        <td>${p.race}</td>
                        <td>${p.fastestlap}</td>
                        <td>${p.total}</td>
                    `;
                    tbody.appendChild(tr);
                 });
            })
            .catch(err => console.error(err));
    }





}

