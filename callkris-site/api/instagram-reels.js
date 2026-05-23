const fs = require("fs");
const path = require("path");

const GRAPH_VERSION = "v21.0";
const BOT_UA = "facebookexternalhit/1.1";
const IG_APP_ID = "936619743392459";
const DEFAULT_USERNAME = "kriskereluk";
const MAX_REELS = 8;

function decodeHtml(value) {
  return value
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, num) => String.fromCharCode(Number(num)));
}

function readFallbackConfig() {
  try {
    const filePath = path.join(process.cwd(), "assets/data/instagram-reels.json");
    const raw = fs.readFileSync(filePath, "utf8");
    return JSON.parse(raw);
  } catch {
    return { profile: "https://www.instagram.com/kriskereluk/", reels: [] };
  }
}

function reelCaption(node) {
  const edges = node.edge_media_to_caption?.edges || [];
  if (!edges.length) {
    return "";
  }
  return edges[0].node?.text || "";
}

async function fetchGraphReels(token, userId) {
  const fields = [
    "id",
    "caption",
    "media_type",
    "media_product_type",
    "thumbnail_url",
    "permalink",
    "timestamp",
  ].join(",");

  const url =
    "https://graph.facebook.com/" +
    GRAPH_VERSION +
    "/" +
    userId +
    "/media?fields=" +
    fields +
    "&limit=24&access_token=" +
    encodeURIComponent(token);

  const response = await fetch(url);
  const payload = await response.json();

  if (!response.ok || !payload.data) {
    throw new Error(payload.error?.message || "Instagram Graph API request failed");
  }

  return payload.data
    .filter(function (item) {
      return item.media_product_type === "REELS" || item.media_type === "VIDEO";
    })
    .slice(0, MAX_REELS)
    .map(function (item) {
      return {
        id: item.id,
        permalink: item.permalink,
        thumbnail_url: item.thumbnail_url || null,
        caption: item.caption || "",
        timestamp: item.timestamp || null,
      };
    });
}

async function fetchPublicProfileReels(username) {
  const response = await fetch(
    "https://www.instagram.com/api/v1/users/web_profile_info/?username=" +
      encodeURIComponent(username),
    {
      headers: {
        "X-IG-App-ID": IG_APP_ID,
        Accept: "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        Referer: "https://www.instagram.com/" + username + "/",
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      },
    }
  );

  const text = await response.text();
  if (!text) {
    throw new Error("Instagram returned an empty response");
  }

  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new Error("Instagram returned an invalid response");
  }

  if (!response.ok) {
    throw new Error(payload.message || "Instagram profile request failed");
  }

  const edges = payload.data?.user?.edge_owner_to_timeline_media?.edges || [];

  return edges
    .map(function (edge) {
      return edge.node;
    })
    .filter(function (node) {
      return node.is_video && node.product_type === "clips";
    })
    .slice(0, MAX_REELS)
    .map(function (node) {
      return {
        id: node.id,
        permalink: "https://www.instagram.com/reel/" + node.shortcode + "/",
        thumbnail_url: node.display_url || node.thumbnail_src || null,
        caption: reelCaption(node),
        timestamp: node.taken_at_timestamp
          ? new Date(node.taken_at_timestamp * 1000).toISOString()
          : null,
      };
    });
}

async function fetchReelMeta(permalink) {
  const response = await fetch(permalink, {
    headers: { "User-Agent": BOT_UA },
  });

  if (!response.ok) {
    return { permalink, thumbnail_url: null, caption: "" };
  }

  const html = await response.text();
  const imageMatch = html.match(/property="og:image" content="([^"]+)"/i);
  const titleMatch = html.match(/property="og:title" content="([^"]+)"/i);

  return {
    permalink,
    thumbnail_url: imageMatch ? decodeHtml(imageMatch[1]) : null,
    caption: titleMatch ? decodeHtml(titleMatch[1]) : "",
  };
}

function readStaticReels(config) {
  return (config.reels || [])
    .slice(0, MAX_REELS)
    .map(function (entry) {
      if (typeof entry === "string") {
        return { permalink: entry, thumbnail_url: null, caption: "" };
      }
      return {
        permalink: entry.permalink,
        thumbnail_url: entry.thumbnail_url || null,
        caption: entry.caption || "",
      };
    });
}

async function fetchFallbackReels(config) {
  const entries = (config.reels || []).slice(0, MAX_REELS);
  if (!entries.length) {
    return [];
  }

  return Promise.all(
    entries.map(function (entry) {
      if (typeof entry === "string") {
        return fetchReelMeta(entry);
      }
      if (entry.thumbnail_url) {
        return Promise.resolve({
          permalink: entry.permalink,
          thumbnail_url: entry.thumbnail_url,
          caption: entry.caption || "",
        });
      }
      return fetchReelMeta(entry.permalink);
    })
  );
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=86400");

  const token = process.env.INSTAGRAM_ACCESS_TOKEN;
  const userId = process.env.INSTAGRAM_USER_ID;
  const fallbackConfig = readFallbackConfig();
  const username = process.env.INSTAGRAM_USERNAME || fallbackConfig.username || DEFAULT_USERNAME;
  const profile =
    fallbackConfig.profile || "https://www.instagram.com/" + username + "/";

  try {
    if (token && userId) {
      const reels = await fetchGraphReels(token, userId);
      return res.status(200).json({
        profile,
        source: "graph-api",
        reels,
      });
    }

    const reels = await fetchPublicProfileReels(username);
    if (reels.length) {
      return res.status(200).json({
        profile,
        source: "public-profile",
        reels,
      });
    }

    const fallbackReels = readStaticReels(fallbackConfig);
    if (fallbackReels.length) {
      return res.status(200).json({
        profile,
        source: "static",
        reels: fallbackReels,
      });
    }

    const enrichedReels = await fetchFallbackReels(fallbackConfig);
    return res.status(200).json({
      profile,
      source: "fallback",
      reels: enrichedReels,
    });
  } catch (error) {
    const fallbackReels = readStaticReels(fallbackConfig);
    if (fallbackReels.length) {
      return res.status(200).json({
        profile,
        source: "static",
        reels: fallbackReels,
        error: error.message,
      });
    }

    try {
      const enrichedReels = await fetchFallbackReels(fallbackConfig);
      return res.status(200).json({
        profile,
        source: "fallback",
        reels: fallbackReels,
        error: error.message,
      });
    } catch {
      return res.status(200).json({
        profile,
        source: "fallback",
        reels: [],
        error: error.message,
      });
    }
  }
};
