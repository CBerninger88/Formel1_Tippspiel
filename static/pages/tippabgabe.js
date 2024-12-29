export function initTippabgabePage(){
    console.log('HomeSeite Initialisierung')
    const nameSelect = document.getElementById('name');
    const citySelect = document.getElementById('city');
    const driver1Select = document.getElementById('driver1');
    const driver2Select = document.getElementById('driver2');
    const driver3Select = document.getElementById('driver3');
    const saveButton = document.getElementById('save');

    nameSelect.addEventListener('change', fetchSelection);
    citySelect.addEventListener('change', fetchSelection);
    saveButton.addEventListener('click', saveSelection);

    // Initiales Laden der gespeicherten Auswahl
    citySelect.dispatchEvent(new Event('change'));

    // Event-Listener für das Ändern der Stadt oder Saison
    function fetchSelection() {
        const selectedName = nameSelect.value;
        const selectedCity = citySelect.value;

        fetch(`/get_selection?name=${selectedName}&city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                driver1Select.value = data.driver1 || "Fahrer";
                driver2Select.value = data.driver2 || "Fahrer";
                driver3Select.value = data.driver3 || "Fahrer";
            });
    }

    // Event-Listener für den Klick auf den Speicher-Button
    function saveSelection() {
        const name = nameSelect.value;
        const city = citySelect.value;
        const driver1 = driver1Select.value;
        const driver2 = driver2Select.value;
        const driver3 = driver3Select.value;

        fetch('/save_selection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, city, driver1, driver2, driver3 }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selection saved successfully!');
            }
        });
    }
}