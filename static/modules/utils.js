export function toggleDropdown(dropdown, dropdownLi) {



    var rect = dropdownLi.getBoundingClientRect();
    // Berechne die Position des Dropdown-Menüs relativ zum Viewport
    var dropdownTop = rect.bottom + window.scrollY;  // Top-Position des Dropdowns
    var dropdownLeft = rect.left + window.scrollX;   // Left-Position des Dropdowns


    dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
    dropdown.style.top = dropdownTop + 'px';
    dropdown.style.left = dropdownLeft + 'px';
}