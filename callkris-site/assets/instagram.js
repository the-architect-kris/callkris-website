(function () {
  "use strict";

  var row = document.querySelector("[data-instagram-row]");
  if (!row) {
    return;
  }

  var track = row.querySelector(".instagram-row__track");
  var profileUrl = "https://www.instagram.com/kriskereluk/";
  var STATIC_FEED = "/assets/data/instagram-reels.json";
  var modal = null;
  var modalFrame = null;

  renderSkeletons(5);
  ensureModal();

  loadStaticFeed()
    .then(function (data) {
      if (data.reels && data.reels.length) {
        return data;
      }
      return loadApiFeed();
    })
    .then(renderFeed)
    .catch(function () {
      track.innerHTML = "";
      track.classList.add("instagram-row__track--empty");
      renderEmptyState();
    });

  function loadStaticFeed() {
    return fetch(STATIC_FEED).then(function (response) {
      if (!response.ok) {
        throw new Error("Static feed unavailable");
      }
      return response.json();
    });
  }

  function loadApiFeed() {
    return fetch("/api/instagram-reels/").then(function (response) {
      if (!response.ok) {
        throw new Error("API feed unavailable");
      }
      return response.json();
    });
  }

  function renderFeed(data) {
    profileUrl = data.profile || profileUrl;
    var reels = (data.reels || []).filter(function (reel) {
      return reel && reel.permalink;
    });

    track.innerHTML = "";
    track.classList.remove("instagram-row__track--empty");

    if (!reels.length) {
      track.classList.add("instagram-row__track--empty");
      renderEmptyState();
      return;
    }

    reels.forEach(function (reel, index) {
      track.appendChild(createReelCard(reel, index));
    });
  }

  function renderSkeletons(count) {
    track.innerHTML = "";
    for (var i = 0; i < count; i++) {
      var skeleton = document.createElement("div");
      skeleton.className = "instagram-reel instagram-reel--skeleton";
      skeleton.setAttribute("aria-hidden", "true");
      track.appendChild(skeleton);
    }
  }

  function renderEmptyState() {
    var empty = document.createElement("div");
    empty.className = "instagram-row__empty";
    empty.innerHTML =
      '<p>Follow <a href="' +
      profileUrl +
      '" target="_blank" rel="noopener noreferrer">@kriskereluk</a> on Instagram for home tours, market updates, and behind-the-scenes.</p>' +
      '<a href="' +
      profileUrl +
      'reels/" class="btn btn--primary" target="_blank" rel="noopener noreferrer">Watch reels on Instagram</a>';
    track.appendChild(empty);
  }

  function createReelCard(reel, index) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "instagram-reel";
    button.setAttribute("aria-label", "Play " + reelCaption(reel, index));

    var thumbSrc = reel.thumbnail || reel.thumbnail_url;
    if (thumbSrc) {
      var img = document.createElement("img");
      img.src = thumbSrc;
      img.alt = "";
      img.loading = index < 2 ? "eager" : "lazy";
      img.decoding = "async";
      button.appendChild(img);
    } else {
      var placeholder = document.createElement("div");
      placeholder.className = "instagram-reel__placeholder";
      placeholder.setAttribute("aria-hidden", "true");
      button.appendChild(placeholder);
    }

    var play = document.createElement("span");
    play.className = "instagram-reel__play";
    play.setAttribute("aria-hidden", "true");
    play.innerHTML =
      '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.14v13.72L19 12 8 5.14z"/></svg>';
    button.appendChild(play);

    button.addEventListener("click", function () {
      openReel(reel);
    });

    return button;
  }

  function reelCaption(reel, index) {
    if (reel.caption) {
      return reel.caption.replace(/\s+/g, " ").trim().slice(0, 120);
    }
    return "Instagram reel " + (index + 1) + " from @kriskereluk";
  }

  function reelShortcode(reel) {
    if (reel.shortcode) {
      return reel.shortcode;
    }
    var match = reel.permalink.match(/\/reel\/([^/]+)/);
    return match ? match[1] : "";
  }

  function ensureModal() {
    modal = document.createElement("div");
    modal.className = "instagram-modal";
    modal.hidden = true;
    modal.innerHTML =
      '<div class="instagram-modal__backdrop" data-instagram-close></div>' +
      '<div class="instagram-modal__dialog" role="dialog" aria-modal="true" aria-label="Instagram reel">' +
      '<button type="button" class="instagram-modal__close" data-instagram-close aria-label="Close reel">&times;</button>' +
      '<div class="instagram-modal__frame-wrap">' +
      '<iframe class="instagram-modal__frame" title="Instagram reel player" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen loading="lazy"></iframe>' +
      "</div>" +
      '<a class="instagram-modal__link" target="_blank" rel="noopener noreferrer">Open on Instagram</a>' +
      "</div>";
    document.body.appendChild(modal);

    modalFrame = modal.querySelector(".instagram-modal__frame");
    modal.querySelectorAll("[data-instagram-close]").forEach(function (el) {
      el.addEventListener("click", closeReel);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && modal && !modal.hidden) {
        closeReel();
      }
    });
  }

  function openReel(reel) {
    var shortcode = reelShortcode(reel);
    if (!shortcode || !modal || !modalFrame) {
      window.open(reel.permalink, "_blank", "noopener,noreferrer");
      return;
    }

    modalFrame.src = "https://www.instagram.com/reel/" + shortcode + "/embed";
    modal.querySelector(".instagram-modal__link").href = reel.permalink;
    modal.hidden = false;
    document.body.classList.add("instagram-modal-open");
    modal.querySelector(".instagram-modal__close").focus();
  }

  function closeReel() {
    if (!modal || !modalFrame) {
      return;
    }
    modal.hidden = true;
    modalFrame.src = "";
    document.body.classList.remove("instagram-modal-open");
  }
})();
