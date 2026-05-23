(function () {
  "use strict";

  var row = document.querySelector("[data-instagram-row]");
  if (!row) {
    return;
  }

  var track = row.querySelector(".instagram-row__track");
  var profileUrl = "https://www.instagram.com/kriskereluk/";

  renderSkeletons(5);

  fetch("/api/instagram-reels")
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      profileUrl = data.profile || profileUrl;
      var reels = (data.reels || []).filter(function (reel) {
        return reel && reel.permalink;
      });

      track.innerHTML = "";

      if (!reels.length) {
        renderEmptyState();
        return;
      }

      reels.forEach(function (reel, index) {
        track.appendChild(createReelCard(reel, index));
      });
    })
    .catch(function () {
      track.innerHTML = "";
      renderEmptyState();
    });

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
    var link = document.createElement("a");
    link.className = "instagram-reel";
    link.href = reel.permalink;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", reelCaption(reel, index));

    if (reel.thumbnail_url) {
      var img = document.createElement("img");
      img.src = reel.thumbnail_url;
      img.alt = "";
      img.loading = index < 2 ? "eager" : "lazy";
      img.decoding = "async";
      link.appendChild(img);
    } else {
      var placeholder = document.createElement("div");
      placeholder.className = "instagram-reel__placeholder";
      placeholder.setAttribute("aria-hidden", "true");
      link.appendChild(placeholder);
    }

    var play = document.createElement("span");
    play.className = "instagram-reel__play";
    play.setAttribute("aria-hidden", "true");
    play.innerHTML =
      '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.14v13.72L19 12 8 5.14z"/></svg>';
    link.appendChild(play);

    return link;
  }

  function reelCaption(reel, index) {
    if (reel.caption) {
      return reel.caption.replace(/\s+/g, " ").trim().slice(0, 120);
    }
    return "Instagram reel " + (index + 1) + " from @kriskereluk";
  }
})();
