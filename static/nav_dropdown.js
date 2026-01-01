const dropdowns = document.querySelectorAll('.dropbtn');

dropdowns.forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();

        // Alle Dropdowns schließen
        document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none');

        const dropdownId = btn.dataset.dropdown;
        const dropdown = document.getElementById(dropdownId);
        if(dropdown) {
            // Absolute Position berechnen
            const rect = btn.getBoundingClientRect();
            const scrollLeft = window.scrollX || document.documentElement.scrollLeft;
            const scrollTop = window.scrollY || document.documentElement.scrollTop;

            // Dropdown direkt unter dem Button positionieren
            dropdown.style.position = 'absolute';
            dropdown.style.left = (rect.left + scrollLeft) + 'px';
            dropdown.style.top = (rect.bottom + scrollTop) + 'px';
            dropdown.style.display = 'block';
        }
    });
});

// Klick außerhalb schließt Dropdowns
document.addEventListener('click', function(e) {
    if(!e.target.closest('.dropbtn') && !e.target.closest('.dropdown-content')) {
        document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none');
    }
});

// Window resize schließt Dropdowns (optional)
window.addEventListener('resize', () => {
    document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none');
});
