/* Early progressive-enhancement gate. Load synchronously in the head,
   before the manuscript is parsed, so Safari never paints raw source first.
   With JavaScript disabled this file never runs and the full HTML stays readable. */
document.documentElement.classList.add("book-hydrating");
// A failed/missing compositor must not leave an empty document permanently.
setTimeout(() => document.documentElement.classList.remove("book-hydrating"), 12000);
