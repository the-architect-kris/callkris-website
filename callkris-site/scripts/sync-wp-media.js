#!/usr/bin/env node
/**
 * Download WordPress media from the legacy SiteGround server into
 * wp-content/uploads/ so the static Vercel site can serve them.
 *
 * After DNS moved to Vercel, callkris.ca/wp-content/* returned 403 because
 * the files were never copied. The SiteGround origin still has the media until
 * that hosting account is removed.
 *
 * Run before deploy: node scripts/sync-wp-media.js
 */

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const SITE_ROOT = path.join(__dirname, "..");
const OUT_DIR = path.join(SITE_ROOT, "wp-content/uploads");
const ORIGIN_IP = process.env.WP_ORIGIN_IP || "35.206.125.188";
const ORIGIN_HOST = process.env.WP_ORIGIN_HOST || "callkris.ca";

function collectMediaPaths() {
  const paths = new Set();

  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
        continue;
      }
      if (!entry.name.endsWith(".html")) {
        continue;
      }
      const html = fs.readFileSync(fullPath, "utf8");
      const matches = html.matchAll(/wp-content\/uploads\/([^"'\s>]+)/g);
      for (const match of matches) {
        paths.add(match[1]);
      }
    }
  }

  walk(SITE_ROOT);
  return [...paths].sort();
}

function downloadFile(relativePath) {
  const url =
    "https://" +
    ORIGIN_HOST +
    "/wp-content/uploads/" +
    encodeURI(relativePath).replace(/%2F/g, "/");
  const outPath = path.join(OUT_DIR, relativePath);

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  execFileSync(
    "curl",
    [
      "-sfL",
      "--resolve",
      ORIGIN_HOST + ":443:" + ORIGIN_IP,
      "-o",
      outPath,
      url,
    ],
    { stdio: "pipe" }
  );

  const size = fs.statSync(outPath).size;
  if (size < 100) {
    throw new Error("Download too small for " + relativePath);
  }
}

function main() {
  const mediaPaths = collectMediaPaths();
  if (!mediaPaths.length) {
    console.log("No wp-content/uploads references found in HTML.");
    return;
  }

  fs.mkdirSync(OUT_DIR, { recursive: true });
  console.log(
    "Syncing " +
      mediaPaths.length +
      " file(s) from " +
      ORIGIN_HOST +
      " (" +
      ORIGIN_IP +
      ")"
  );

  for (const relativePath of mediaPaths) {
    downloadFile(relativePath);
    console.log("  " + relativePath);
  }

  console.log("Done.");
}

try {
  main();
} catch (error) {
  console.error(error.message || error);
  process.exit(1);
}
