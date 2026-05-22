/* ==========================================================================
   callkris.ca — site interactions
   - Mobile navigation drawer
   - Sticky header shadow on scroll
   - Contact form submission via Web3Forms (no page reload)
   ========================================================================== */
(function () {
  "use strict";

  /* ---- Mobile navigation ---- */
  var toggle = document.querySelector(".nav__toggle");
  var menu = document.querySelector(".nav__menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("is-open");
      document.body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---- Header shadow on scroll ---- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- Current year in footer ---- */
  var yearEl = document.querySelector("[data-year]");
  if (yearEl) { yearEl.textContent = new Date().getFullYear(); }

  /* ==========================================================================
     Web3Forms contact forms
     --------------------------------------------------------------------------
     Each form with [data-web3forms] is submitted via fetch so the visitor
     stays on the page. To activate: create a free access key at
     https://web3forms.com (it sends submissions to hello@callkris.ca) and
     paste it into the value of the hidden "access_key" input in every form.
     ========================================================================== */
  var ACCESS_KEY_PLACEHOLDER = "YOUR_WEB3FORMS_ACCESS_KEY";
  var forms = document.querySelectorAll("form[data-web3forms]");

  forms.forEach(function (form) {
    var status = form.querySelector(".form-status");
    var submitBtn = form.querySelector("[type=submit]");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!status) { return; }

      var keyField = form.querySelector('input[name="access_key"]');
      if (!keyField || keyField.value === ACCESS_KEY_PLACEHOLDER || !keyField.value) {
        showStatus(status, "error",
          "This form isn't connected yet. Add your Web3Forms access key to enable it.");
        return;
      }

      var btnText = submitBtn ? submitBtn.textContent : "";
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "Sending…"; }

      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form)
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data && data.success) {
            showStatus(status, "success",
              "Thanks — your message is on its way. Kris will be in touch shortly.");
            form.reset();
          } else {
            showStatus(status, "error",
              "Something went wrong. Please call or text 778-288-4481.");
          }
        })
        .catch(function () {
          showStatus(status, "error",
            "Network error. Please call or text 778-288-4481.");
        })
        .finally(function () {
          if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = btnText; }
        });
    });
  });

  function showStatus(el, type, msg) {
    el.textContent = msg;
    el.className = "form-status is-" + type;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
  }
})();
