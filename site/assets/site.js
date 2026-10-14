// Color scheme is owned by the browser/app via prefers-color-scheme.
const estateNav = document.querySelector('[data-site-nav]');
if (estateNav && !estateNav.hasAttribute('data-open')) estateNav.dataset.open = 'false';
