#!/usr/bin/env node
/* Browser proof for the original-image semantic Bookshelf fixture. */
import fs from "node:fs";
import path from "node:path";
const BASE = process.env.VISUAL_FIXTURE_BASE || "http://127.0.0.1:8199";
const ROUTE = "/fixtures/semantic-visual-bookshelf/";
const CDP = process.env.CHROME_CDP || "http://127.0.0.1:9237";
const OUTPUT = process.env.VISUAL_FIXTURE_CAPTURE || "/tmp/semantic-visual-bookshelf";
fs.mkdirSync(OUTPUT, { recursive: true });
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const slug = "reframe-and-the-business-value-of-the-estate";
const teatro = "teatro-an-unfinished-composition";
const workSelector = id => '[data-book-id="' + id + '"] a.shelf-book';
async function scenario(label, width, height) {
  const tab = await (await fetch(CDP + "/json/new?about:blank", { method: "PUT" })).json();
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise(resolve => ws.addEventListener("open", resolve, { once: true }));
  let counter = 0;
  const pending = new Map();
  ws.addEventListener("message", event => {
    const message = JSON.parse(event.data);
    if (pending.has(message.id)) {
      pending.get(message.id)(message);
      pending.delete(message.id);
    }
  });
  const command = (method, params = {}) => new Promise(resolve => {
    const id = ++counter;
    pending.set(id, resolve);
    ws.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => {
    const response = await command("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (response.result.exceptionDetails) throw new Error(JSON.stringify(response.result.exceptionDetails));
    return response.result.result.value;
  };
  const wait = async expression => {
    for (let attempt = 0; attempt < 90; attempt++) {
      if (await evaluate(expression)) return;
      await sleep(150);
    }
    throw new Error("Wait timed out: " + expression);
  };
  const navigate = async url => {
    await command("Page.navigate", { url: BASE + url });
    await wait("location.pathname===" + JSON.stringify(url.split("#")[0]));
  };
  const click = async selector => {
    const rect = await evaluate("document.querySelector(" + JSON.stringify(selector) + ")?.getBoundingClientRect().toJSON()");
    if (!rect || rect.width < 16 || rect.height < 16) throw new Error("Invisible click target " + selector);
    const x = rect.x + rect.width / 2, y = rect.y + rect.height / 2;
    await command("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
    await command("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
  };
  const key = async key => {
    const code = key === "ArrowRight" ? 39 : key === "ArrowLeft" ? 37 : 27;
    await command("Input.dispatchKeyEvent", { type: "keyDown", key, code: key, windowsVirtualKeyCode: code });
    await command("Input.dispatchKeyEvent", { type: "keyUp", key, code: key, windowsVirtualKeyCode: code });
  };
  const shot = async step => {
    const result = await command("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    fs.writeFileSync(path.join(OUTPUT, label + "-" + step + ".png"), Buffer.from(result.result.data, "base64"));
  };
  const loaded = selector => "(()=>{const images=[...document.querySelectorAll(" + JSON.stringify(selector) +
    ")];return images.length>0&&images.every(image=>image.complete&&image.naturalWidth>0)})()";
  try {
    await command("Page.enable");
    await command("Runtime.enable");
    await command("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await navigate(ROUTE);
    await wait(loaded(".shelf-book img"));
    const root = await evaluate('({books:document.querySelectorAll(".shelf-book").length,empties:document.querySelectorAll(".bookshelf-empty").length,logo:!!document.querySelector(".bookshelf-brand img")?.naturalWidth,labels:document.querySelectorAll(".shelf-cover-name").length,overflow:document.documentElement.scrollWidth>innerWidth})');
    if (root.books !== 2 || root.empties !== 20 || !root.logo || root.labels || root.overflow) throw new Error("Root visual shelf invalid " + JSON.stringify(root));
    await shot("estate");
    await click(workSelector("essays"));
    await wait('document.body?.dataset.collectionId==="essays"');
    await wait(loaded(".shelf-book img"));
    const essays = await evaluate('({books:document.querySelectorAll(".shelf-book").length,empties:document.querySelectorAll(".bookshelf-empty").length,collection:document.body.dataset.collectionId,labels:document.querySelectorAll(".shelf-cover-name").length})');
    if (essays.books !== 3 || essays.empties !== 20 || essays.labels) throw new Error("Essay collection invalid " + JSON.stringify(essays));
    await shot("essays");
    await click(workSelector(slug));
    await wait('document.body?.dataset.workId===' + JSON.stringify(slug));
    await wait(loaded(".visual-page:not([hidden]) img"));
    const first = await evaluate('({count:document.querySelectorAll(".visual-page").length,shown:document.querySelectorAll(".visual-page:not([hidden])").length,source:document.body.dataset.sourceSha256,collection:document.body.dataset.collectionId,back:document.querySelector(".visual-return")?.getAttribute("href"),prose:document.querySelectorAll("article,.book-prose,.shelf-cover-name").length,overflow:document.documentElement.scrollWidth>innerWidth})');
    if (first.count !== 3 || first.shown !== 1 || first.collection !== "essays" ||
        !first.back.endsWith("/collections/essays/#work-" + slug) || first.prose || first.overflow ||
        !/^[a-f0-9]{64}$/.test(first.source)) throw new Error("Visual reader invalid " + JSON.stringify(first));
    await shot("reader-first");
    await key("ArrowRight");
    await wait('location.hash==="#plate-2" && document.querySelector("#plate-2")?.hidden===false');
    await wait(loaded(".visual-page:not([hidden]) img"));
    await shot("reader-second");
    await evaluate("history.back()");
    await wait('document.querySelector("#plate-1")?.hidden===false && location.hash===""');
    const box = await evaluate('document.querySelector("#visual-book").getBoundingClientRect().toJSON()');
    const y = box.y + box.height / 2, start = Math.min(box.right - 35, box.x + box.width * 0.75);
    await command("Input.dispatchMouseEvent", { type: "mousePressed", x: start, y, button: "left", clickCount: 1 });
    await command("Input.dispatchMouseEvent", { type: "mouseMoved", x: start - 110, y, button: "left" });
    await command("Input.dispatchMouseEvent", { type: "mouseReleased", x: start - 130, y, button: "left", clickCount: 1 });
    await wait('location.hash==="#plate-2"');
    await click("#visual-next");
    await wait('location.hash==="#plate-3" && document.querySelector("#visual-next").disabled');
    await navigate(ROUTE + "collections/essays/works/" + slug + "/#plate-99");
    await wait('document.querySelector("#visual-book")?.dataset.invalid==="true"');
    const invalid = await evaluate('({shown:document.querySelectorAll(".visual-page:not([hidden])").length,next:document.querySelector("#visual-next").disabled,prev:document.querySelector("#visual-previous").disabled})');
    if (invalid.shown || !invalid.next || !invalid.prev) throw new Error("Unknown plate silently admitted");
    await navigate(ROUTE + "collections/essays/works/" + slug + "/#plate-3");
    await wait('document.querySelector("#plate-3")?.hidden===false');
    await key("Escape");
    await wait('document.body?.dataset.collectionId==="essays" && location.hash==="#work-' + slug + '"');
    await navigate(ROUTE);
    await wait(loaded(".shelf-book img"));
    await click(workSelector("first-readings"));
    await wait('document.body?.dataset.collectionId==="first-readings"');
    await wait(loaded(".shelf-book img"));
    await shot("first-readings");
    await click(workSelector(teatro));
    await wait('document.body?.dataset.workId===' + JSON.stringify(teatro));
    await wait(loaded(".visual-page:not([hidden]) img"));
    const hearing = await evaluate('({collection:document.body.dataset.collectionId,count:document.querySelectorAll(".visual-page").length,source:document.querySelector(".visual-page")?.dataset.assetSha256,parent:document.querySelector(".visual-return")?.getAttribute("href"),next:document.querySelector("#visual-next").disabled})');
    if (hearing.collection !== "first-readings" || hearing.count !== 1 || !hearing.next ||
        !hearing.parent.endsWith("/collections/first-readings/#work-" + teatro)) throw new Error("Nested identity invalid " + JSON.stringify(hearing));
    await shot("first-reading-visual");
    await click(".visual-return");
    await wait('document.body?.dataset.collectionId==="first-readings" && location.hash==="#work-' + teatro + '"');
    console.log("VISUAL_BOOKSHELF_BROWSER_PASS", label, JSON.stringify({ root, essays, first, invalid, hearing, history: true, keyboard: true, pointer: true }));
  } finally {
    ws.close();
    await fetch(CDP + "/json/close/" + tab.id).catch(() => {});
  }
}
for (const shape of [["ipad-portrait", 820, 1180], ["ipad-landscape", 1180, 820], ["phone-portrait", 390, 844]]) {
  await scenario(...shape);
}
