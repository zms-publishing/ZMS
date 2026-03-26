/*
 * ZMS Grayscale theme behavior.
 * Adapted from the Start Bootstrap Grayscale navbar pattern.
 */

window.addEventListener('DOMContentLoaded', function() {
	var navbar = document.body.querySelector('#mainNav');
	if (!navbar) {
		return;
	}

	var navbarShrink = function() {
		if (window.scrollY > 24) {
			navbar.classList.add('navbar-shrink');
		} else {
			navbar.classList.remove('navbar-shrink');
		}
	};

	navbarShrink();
	document.addEventListener('scroll', navbarShrink);

	var navbarToggler = document.body.querySelector('.navbar-toggler');
	var responsiveNavItems = [].slice.call(document.querySelectorAll('#navbarResponsive .nav-link'));
	responsiveNavItems.forEach(function(responsiveNavItem) {
		responsiveNavItem.addEventListener('click', function() {
			if (!navbarToggler) {
				return;
			}
			if (window.getComputedStyle(navbarToggler).display !== 'none') {
				navbarToggler.click();
			}
		});
	});
});