(function () {
  "use strict";

  // Mobile navigation toggle
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Dismissible flash messages (auto-hide after a few seconds)
  document.querySelectorAll(".message").forEach(function (msg) {
    var close = msg.querySelector("[data-dismiss]");
    if (close) {
      close.addEventListener("click", function () { msg.remove(); });
    }
    setTimeout(function () { msg.remove(); }, 6000);
  });

  // Confirm destructive actions
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!window.confirm(form.getAttribute("data-confirm"))) {
        event.preventDefault();
      }
    });
  });

  // Give posters without an image a stable colour derived from the title
  document.querySelectorAll(".poster[data-seed]").forEach(function (poster) {
    var seed = poster.getAttribute("data-seed") || "";
    var hash = 0;
    for (var i = 0; i < seed.length; i++) {
      hash = (hash * 31 + seed.charCodeAt(i)) % 360;
    }
    poster.style.setProperty("--hue", hash);
  });
})();
