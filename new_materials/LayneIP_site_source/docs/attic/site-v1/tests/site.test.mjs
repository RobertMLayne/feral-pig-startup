import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const pages = ["index.html", "professionals.html", "insights.html", "systems.html"];

test("all primary pages have unique titles and core navigation", async () => {
  const titles = [];
  for (const page of pages) {
    const html = await readFile(new URL(`../${page}`, import.meta.url), "utf8");
    assert.match(html, /<title>[^<]+<\/title>/);
    assert.match(html, /professionals\.html/);
    assert.match(html, /insights\.html/);
    assert.match(html, /systems\.html/);
    assert.match(html, /data-consultation/);
    titles.push(html.match(/<title>([^<]+)<\/title>/)[1]);
  }
  assert.equal(new Set(titles).size, pages.length);
});

test("professional directory is searchable and safely labels unverified details", async () => {
  const html = await readFile(new URL("../professionals.html", import.meta.url), "utf8");
  assert.match(html, /data-professional-search/);
  assert.match(html, /data-professional-filter/);
  assert.match(html, /Robert M\. Layne, Ph\.D\./);
  assert.match(html, /will be verified before public launch/i);
});

test("planned subdomains are represented without implying they are live", async () => {
  const insights = await readFile(new URL("../insights.html", import.meta.url), "utf8");
  const systems = await readFile(new URL("../systems.html", import.meta.url), "utf8");
  assert.match(insights, /Planned publishing home/);
  assert.match(insights, /insights\.layneip\.com/);
  assert.match(systems, /Planned software home/);
  assert.match(systems, /systems\.layneip\.com/);
});
