/*
 * ZMS Virtum theme behavior.
 * Handles mobile menu toggling and sticky header mode.
 */

window.addEventListener('DOMContentLoaded', function() {
	var header = document.querySelector('.virtum-header');
	var toggle = document.querySelector('.menu-toggle');
	var nav = document.querySelector('.site-nav');

	if (toggle && nav) {
		toggle.addEventListener('click', function() {
			var expanded = toggle.getAttribute('aria-expanded') === 'true';
			toggle.setAttribute('aria-expanded', expanded ? 'false' : 'true');
			nav.classList.toggle('open', !expanded);
		});
	}

	var setStickyMode = function() {
		if (!header) {
			return;
		}
		if (window.scrollY > 24) {
			document.body.classList.add('virtum-scrolled');
		} else {
			document.body.classList.remove('virtum-scrolled');
		}
	};

	setStickyMode();
	document.addEventListener('scroll', setStickyMode);
});
