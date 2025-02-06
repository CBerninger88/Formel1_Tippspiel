document.addEventListener('DOMContentLoaded', function() {

    console.log('Allgemeine Initialisierung');

    const pageIdentifier = document.body.getAttribute('data-page-id');

    switch(pageIdentifier) {
        case 'home':
            import('./pages/home.js').then(module => {
                module.initHomePage();
            });
            break;

        case 'tippabgabe':
            import('./pages/tippabgabe.js').then(module => {
                module.initTippabgabePage();
            });
            break;

        case 'sprinttipps':
            import('./pages/sprinttipps.js').then(module => {
                module.initSprinttippsPage();
            });
            break;

        case 'wmStand':
            import('./pages/wmStand.js').then(module => {
                module.initwmStandPage();
            });
            break;

        case 'rennergebnis':
            import('./pages/rennergebnis.js').then(module => {
                module.initRennergebnisPage();
            });

        default:
            console.log('Keine spezielle Initialisierung erforderlich');
    }

    // Dropdown-Logik einbinden
    import('./modules/utils.js').then(({ toggleDropdown }) => {

        // Hilfsfunktion zur Initialisierung eines Dropdowns
        function initDropdown(toggleId, dropdownId, liId) {
            const toggleButton = document.getElementById(toggleId);
            const dropdownMenu = document.getElementById(dropdownId);
            const listItem = document.getElementById(liId)

            if (toggleButton && dropdownMenu && listItem) {
                toggleButton.addEventListener('click', function() {
                    toggleDropdown(dropdownMenu, listItem);
                });
            }
        }

        // Ergebnis Dropdown intialisieren
        initDropdown('ergDropdownToggle', 'ergDropdownMenu', 'ergDropdownLi');

        // Tippabgabe Dropdown intialisieren
        initDropdown('tippDropdownToggle', 'tippDropdownMenu', 'tippDropdownLi');

    });

});







