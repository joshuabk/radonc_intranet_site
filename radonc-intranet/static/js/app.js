/* Small, dependency-free behaviors. No external requests. */
(function () {
  "use strict";

  // Copy buttons for UNC / file paths in the link hub.
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    var text = btn.getAttribute("data-copy");
    var done = function () {
      var old = btn.textContent;
      btn.textContent = "Copied";
      setTimeout(function () { btn.textContent = old; }, 1400);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done);
    } else {
      // http intranet fallback
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (err) {}
      document.body.removeChild(ta);
    }
  });

  // Huddle board: display mode for wall monitors (?display=1 or the toggle).
  var params = new URLSearchParams(window.location.search);
  if (params.get("display") === "1") document.body.classList.add("display-mode");
  var toggle = document.getElementById("display-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      document.body.classList.toggle("display-mode");
    });
  }

  // Live clock (huddle board).
  var clock = document.getElementById("clock");
  if (clock) {
    var tick = function () {
      clock.textContent = new Date().toLocaleString([], {
        weekday: "short", month: "short", day: "numeric",
        hour: "2-digit", minute: "2-digit", second: "2-digit",
      });
    };
    tick();
    setInterval(tick, 1000);
  }

  // Huddle board auto-refresh every 5 minutes when in display mode.
  if (document.body.dataset.autorefresh === "1") {
    setTimeout(function () { window.location.reload(); }, 5 * 60 * 1000);
  }
})();
