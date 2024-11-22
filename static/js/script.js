/////////// DYNAMIC YEAR COPYRIGHT 
const yearEL = document.querySelector(".year");
const currentDate = new Date().getFullYear();
yearEL.textContent = currentDate;

/////////// MAIN NAV BAR
const btnNavEl = document.querySelector(".btn-mobile-nav");
const sectionNavEl = document.querySelector(".section-nav");

function openNavBar() {
  sectionNavEl.classList.toggle("nav-open");
}

btnNavEl.addEventListener("click", openNavBar);