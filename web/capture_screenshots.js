const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    colorScheme: 'dark' // Assuming the app detects OS dark mode or is dark by default
  });
  
  const page = await context.newPage();
  
  const basePath = path.join(__dirname, '../docs/screenshots');
  if (!fs.existsSync(basePath)){
      fs.mkdirSync(basePath, { recursive: true });
  }

  const routes = [
    { url: 'http://localhost:3001/', file: 'dashboard.png' },
    { url: 'http://localhost:3001/portfolio', file: 'portfolio.png' },
    { url: 'http://localhost:3001/correlation', file: 'correlation.png' },
    { url: 'http://localhost:3001/india-funds', file: 'india_mutual_funds.png' },
    { url: 'http://localhost:3001/screener', file: 'screener.png' },
    { url: 'http://localhost:3001/risk', file: 'risk_analysis.png' },
    { url: 'http://localhost:3001/heatmap', file: 'sector_heatmap.png' },
    { url: 'http://localhost:3001/indices', file: 'sector_indices.png' },
    { url: 'http://localhost:3001/macro', file: 'market_overview.png' },
    { url: 'http://localhost:3001/commodities', file: 'commodities.png' },
    { url: 'http://localhost:3001/forex', file: 'forex.png' },
    { url: 'http://localhost:3001/allocation', file: 'allocation.png' }
  ];

  for (const route of routes) {
    console.log(`Navigating to ${route.url}...`);
    try {
        await page.goto(route.url, { waitUntil: 'networkidle', timeout: 30000 });
        // Give explicit wait for charts to animate and render
        await page.waitForTimeout(4000); 
        await page.screenshot({ path: path.join(basePath, route.file) });
        console.log(`Saved ${route.file}`);
    } catch (e) {
        console.error(`Failed on ${route.url}:`, e);
    }
  }

  await browser.close();
  console.log("Screenshot capture complete.");
})();
