#!/usr/bin/env node
/**
 * Refresh assets/data/instagram-reels.json from @kriskereluk and download
 * thumbnail images locally (Instagram CDN blocks hotlinking on other sites).
 *
 * Run before deploy: node scripts/sync-instagram-reels.js
 */

const fs = require("fs");
const path = require("path");

const IG_APP_ID = "936619743392459";
const USERNAME = process.env.INSTAGRAM_USERNAME || "kriskereluk";
const MAX_REELS = 8;
const OUT_FILE = path.join(__dirname, "../assets/data/instagram-reels.json");
const THUMB_DIR = path.join(__dirname, "../assets/data/instagram/thumbs");

function reelCaption(node) {
  const edges = node.edge_media_to_caption?.edges || [];
  return edges[0]?.node?.text || "";
}

async function downloadThumbnail(url, shortcode) {
  const response = await fetch(url, {
    headers: {
      Referer: "https://www.instagram.com/",
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });

  if (!response.ok) {
    throw new Error("Thumbnail download failed for " + shortcode);
  }

  const contentType = response.headers.get("content-type") || "image/jpeg";
  const ext = contentType.includes("png") ? "png" : "jpg";
  const filename = shortcode + "." + ext;
  const filePath = path.join(THUMB_DIR, filename);
  const buffer = Buffer.from(await response.arrayBuffer());

  fs.writeFileSync(filePath, buffer);
  return "/assets/data/instagram/thumbs/" + filename;
}

async function main() {
  fs.mkdirSync(THUMB_DIR, { recursive: true });

  const response = await fetch(
    "https://www.instagram.com/api/v1/users/web_profile_info/?username=" +
      encodeURIComponent(USERNAME),
    {
      headers: {
        "X-IG-App-ID": IG_APP_ID,
        Accept: "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        Referer: "https://www.instagram.com/" + USERNAME + "/",
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      },
    }
  );

  const text = await response.text();
  let payload;

  try {
    payload = JSON.parse(text);
  } catch {
    console.error("Instagram returned non-JSON response. Try again from a residential network.");
    process.exit(1);
  }

  if (!response.ok || !payload.data?.user) {
    console.error(payload.message || "Instagram profile request failed");
    process.exit(1);
  }

  const nodes = (payload.data.user.edge_owner_to_timeline_media?.edges || [])
    .map(function (edge) {
      return edge.node;
    })
    .filter(function (node) {
      return node.is_video && node.product_type === "clips";
    })
    .slice(0, MAX_REELS);

  const reels = [];

  for (const node of nodes) {
    const shortcode = node.shortcode;
    const remoteThumb = node.display_url || node.thumbnail_src;

    let thumbnail = null;
    if (remoteThumb) {
      try {
        thumbnail = await downloadThumbnail(remoteThumb, shortcode);
        console.log("Saved thumbnail:", thumbnail);
      } catch (error) {
        console.warn(error.message);
      }
    }

    reels.push({
      shortcode,
      permalink: "https://www.instagram.com/reel/" + shortcode + "/",
      thumbnail,
      caption: reelCaption(node).slice(0, 200),
    });
  }

  const output = {
    username: USERNAME,
    profile: "https://www.instagram.com/" + USERNAME + "/",
    synced_at: new Date().toISOString(),
    reels,
  };

  fs.writeFileSync(OUT_FILE, JSON.stringify(output, null, 2) + "\n");
  console.log("Wrote " + reels.length + " reels to " + OUT_FILE);
}

main().catch(function (error) {
  console.error(error.message || error);
  process.exit(1);
});
