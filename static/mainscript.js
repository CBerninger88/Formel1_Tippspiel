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

        case 'tabelle':
            import('./pages/tippabgabe.js').then(module => {
                module.initTabellePage();
            });
            break;

        default:
            console.log('Keine spezielle Initialisierung erforderlich');
    }

});


