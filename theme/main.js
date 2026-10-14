/* tiny progressive enhancements - the site works without this file. */
(function () {
  // front page: show the colour version of a thumbnail on hover / focus,
  // on touch screens when the card scrolls into the middle of the screen.
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  function on(card) {
    var img = card.querySelector("img.color");
    if (img && !img.getAttribute("src") && img.dataset.src) {
      img.addEventListener("load", function () { img.classList.add("loaded"); }, { once: true });
      img.src = img.dataset.src;
    }
    card.classList.add("is-live");
  }
  function off(card) { card.classList.remove("is-live"); }
  cards.forEach(function (card) {
    card.addEventListener("pointerenter", function () { on(card); });
    card.addEventListener("pointerleave", function () { off(card); });
    card.addEventListener("focusin", function () { on(card); });
    card.addEventListener("focusout", function () { off(card); });
  });
  if (window.matchMedia && matchMedia("(hover: none)").matches && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { e.isIntersecting ? on(e.target) : off(e.target); });
    }, { rootMargin: "-42% 0px -42% 0px" });
    cards.forEach(function (c) { io.observe(c); });
  }

  // project pages: arrow keys jump to previous / next project
  document.addEventListener("keydown", function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey || /input|textarea/i.test(e.target.tagName)) return;
    var a = document.querySelector('.pager a[data-key="' + e.key + '"]');
    if (a) location.href = a.href;
  });
})();
