const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    // Listen to all console events
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.error(`[Browser Error] ${msg.text()}`);
        }
    });

    // Listen to page errors (uncaught exceptions)
    page.on('pageerror', exception => {
        console.error(`[Uncaught Exception] ${exception}`);
    });

    console.log("Navigating to /allocation...");
    await page.goto('http://localhost:3000/allocation', { waitUntil: 'networkidle' });

    console.log("Waiting 3 seconds...");
    await page.waitForTimeout(3000);

    console.log("Navigating to /portfolio...");
    await page.goto('http://localhost:3000/portfolio', { waitUntil: 'networkidle' });

    console.log("Waiting for holding to appear...");
    await page.waitForSelector('text=Lump Sum', { timeout: 10000 }).catch(() => console.log("Holding not found"));

    console.log("Expanding first holding...");
    // Try to click the first holding's name to expand
    // In Portfolio, clicking the holding row calls loadDetail
    // The holding name usually has a <span> with font-weight 700
    try {
        const holdingElements = await page.$$('span:has-text("1Y")');
        if (holdingElements.length > 0) {
            await holdingElements[0].click({ force: true });
            await page.waitForTimeout(2000);
        } else {
            console.log("Could not find a holding to click.");
        }
    } catch (err) {
        console.error("Error clicking holding:", err);
    }

    await browser.close();
})();
