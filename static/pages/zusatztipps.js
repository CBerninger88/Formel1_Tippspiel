import { populateDropdowns } from '../modules/utils.js';

export function initZusatztippsPage(){
    console.log('Sprint-Tippabgabe- Seite Initialisierung');

    const tipprundeSelect = document.getElementById('tipprunde-select');

    const wmdriverSelects = Array.from(document.querySelectorAll('[id^="wmdriver"]'));
    const pptrophySelect = document.getElementById('pptrophy');
    const flawardSelect = document.getElementById('flaward');
    const sdwmEntry = document.getElementById('sdwm');
    const siegerEntry = document.getElementById('sieger');
    const teamSelects = Array.from(document.querySelectorAll('[id^="team"]'));
    const saveButton = document.getElementById('save');

    // 1. Dynamische Namen und Städte
    //const tippSpieler = ['Alexander', 'Christine', 'Christoph', 'Jürgen', 'Simon', 'Ergebnis'];
    //populateDropdowns([nameSelect], tippSpieler, 'Name auswählen');


    // 2. Dynamische Fahrer-Dropdowns
    fetch('/get_drivers')
        .then(response => response.json())
        .then(drivers => {
            populateDropdowns(wmdriverSelects, drivers, 'Fahrer auswählen');
            populateDropdowns([pptrophySelect], drivers, 'Fahrer auswählen');
            populateDropdowns([flawardSelect], drivers, 'Fahrer auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Fahrer:', error);
        });



    fetch('/get_teams')
        .then(response => response.json())
        .then(teams => {
            populateDropdowns(teamSelects, teams, 'Team auswählen');
        })
        .catch(error => {
            console.error('Fehler beim Laden der Teams:', error);
        });

    fetchSelection();
    tipprundeSelect.addEventListener('change', fetchSelection);
    saveButton.addEventListener('click', saveSelection);

    // Initiales Laden der gespeicherten Auswahl
    //citySelect.dispatchEvent(new Event('change'));

    // Event-Listener für das Ändern der Stadt oder Saison
    function fetchSelection() {
        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id

        let selectionUrl = `/get_zusatztipps`;

        if (tipprunde_id) {
            selectionUrl += `?tipprunde_id=${tipprunde_id}`;
        }

        fetch(selectionUrl)
            .then(response => response.json())
            .then(data => {
                wmdriverSelects.forEach((wmDriverSelect, index) => {
                   const wmDriverKey = `wmdriver${index + 1}`;
                   wmDriverSelect.value = data[wmDriverKey] || "";
                });
                pptrophySelect.value = data['pptrophydriver'] || "";
                flawardSelect.value = data['flawarddriver'] || "";
                sdwmEntry.value = data['sdwm'] || "";
                siegerEntry.value = data['anzahlsieger'] || "";

                teamSelects.forEach((teamSelect, index) => {
                   const teamKey = `team${index + 1}`;
                   teamSelect.value = data[teamKey] || "";
                });

            });
    }

    // Event-Listener für den Klick auf den Speicher-Button
    function saveSelection() {

        const wmDriverData = wmdriverSelects.map(driver => driver.value);
        const teamData = teamSelects.map(team => team.value);

        const select = document.getElementById('tipprunde-select');
        const option = select.options[select.selectedIndex];
        const tipprunde_id = option.dataset.id;

        // Dictionary mit Keys (driver1, driver2, etc.) generieren
        const wmdriver = {};
        wmDriverData.forEach((driver, index) => {
            wmdriver[`wmdriver${index + 1}`] = driver;
        });

        const pptrophydriver = pptrophySelect.value
        const flawarddriver = flawardSelect.value
        const sdwm = sdwmEntry.value
        const anzahlsieger = siegerEntry.value

        const teams = {};
        teamData.forEach((team, index) => {
            teams[`team${index + 1}`] = team;
        });

        fetch('/save_zusatztipps', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({...wmdriver, pptrophydriver, flawarddriver, sdwm, anzahlsieger, ...teams, tipprunde_id: tipprunde_id ?? null}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }
}