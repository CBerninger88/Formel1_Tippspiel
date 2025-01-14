export function toggleDropdown(dropdown, dropdownLi) {



    var rect = dropdownLi.getBoundingClientRect();
    // Berechne die Position des Dropdown-Menüs relativ zum Viewport
    var dropdownTop = rect.bottom + window.scrollY;  // Top-Position des Dropdowns
    var dropdownLeft = rect.left + window.scrollX;   // Left-Position des Dropdowns


    dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
    dropdown.style.top = dropdownTop + 'px';
    dropdown.style.left = dropdownLeft + 'px';
}


/**
 * Befüllt die angegebenen Dropdowns mit Fahrern.
 * @param {Array} dropdowns - Array von Dropdown-Elementen.
 * @param {Array} fahrerListe - Liste der Fahrer.
 */
export function populateDropdowns(dropdowns, fahrerListe, defaultText = "Auswahl") {
    dropdowns.forEach(select => {
        // Vorherige Optionen entfernen
        select.innerHTML = "";

        // Platzhalter hinzufügen
        const placeholderOption = document.createElement('option');
        placeholderOption.value = "";
        placeholderOption.textContent = defaultText;
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        select.appendChild(placeholderOption);

        // Fahrer hinzufügen
        fahrerListe.forEach(fahrer => {
            const option = document.createElement('option');
            option.value = fahrer;
            option.textContent = fahrer;
            select.appendChild(option);
        });
    });
}