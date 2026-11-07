const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

async function smoothMouseMove(page, targetX, targetY, steps = 25) {
  await page.mouse.move(targetX, targetY, { steps });
}

async function moveAndHover(page, selector, steps = 20) {
  const elem = await page.waitForSelector(selector, { state: 'visible', timeout: 10000 });
  const box = await elem.boundingBox();
  if (box) {
    const x = box.x + box.width / 2;
    const y = box.y + box.height / 2;
    await page.mouse.move(x, y, { steps });
    await new Promise(r => setTimeout(r, 350));
    return { x, y, box };
  }
}

async function moveAndClick(page, selector, steps = 20) {
  await moveAndHover(page, selector, steps);
  await page.click(selector);
  await new Promise(r => setTimeout(r, 400));
}

async function smoothScroll(page, targetY, durationMs = 1200) {
  await page.evaluate(async ({ targetY, durationMs }) => {
    const startY = window.scrollY;
    const diff = targetY - startY;
    const startTime = performance.now();
    await new Promise(resolve => {
      function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / durationMs, 1);
        const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
        window.scrollTo(0, startY + diff * ease);
        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          resolve();
        }
      }
      requestAnimationFrame(step);
    });
  }, { targetY, durationMs });
}

async function injectVirtualCursor(page) {
  await page.evaluate(() => {
    if (document.getElementById('virtual-cursor')) return;
    const cursor = document.createElement('div');
    cursor.id = 'virtual-cursor';
    cursor.style.position = 'fixed';
    cursor.style.width = '20px';
    cursor.style.height = '20px';
    cursor.style.borderRadius = '50%';
    cursor.style.backgroundColor = 'rgba(99, 102, 241, 0.8)';
    cursor.style.border = '2px solid #ffffff';
    cursor.style.boxShadow = '0 0 12px rgba(99, 102, 241, 0.9), 0 2px 6px rgba(0,0,0,0.5)';
    cursor.style.pointerEvents = 'none';
    cursor.style.zIndex = '9999999';
    cursor.style.transition = 'transform 0.1s ease, background-color 0.15s ease';
    cursor.style.transform = 'translate(-50%, -50%)';
    cursor.style.left = '200px';
    cursor.style.top = '150px';
    document.body.appendChild(cursor);

    window.addEventListener('mousemove', (e) => {
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
    });
    window.addEventListener('mousedown', () => {
      cursor.style.transform = 'translate(-50%, -50%) scale(0.75)';
      cursor.style.backgroundColor = 'rgba(239, 68, 68, 0.95)';
    });
    window.addEventListener('mouseup', () => {
      cursor.style.transform = 'translate(-50%, -50%) scale(1)';
      cursor.style.backgroundColor = 'rgba(99, 102, 241, 0.8)';
    });
  });
}

async function runDemo() {
  console.log('--- Starting SSDLC Analyzer 1-Minute Demonstration Recording ---');
  const captureDir = 'C:\\Users\\Thoufeek\\Pictures\\capture';
  if (!fs.existsSync(captureDir)) {
    fs.mkdirSync(captureDir, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: true,
    args: ['--window-size=1280,720', '--disable-gpu']
  });

  const context = await browser.newContext({
    recordVideo: {
      dir: captureDir,
      size: { width: 1280, height: 720 }
    },
    viewport: { width: 1280, height: 720 },
    acceptDownloads: true
  });

  const page = await context.newPage();

  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

  console.log('1. Navigating to SSDLC Analyzer Web Platform...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
  await injectVirtualCursor(page);

  // 0:00 - 0:08 (8s) Initial view & platform inspection
  console.log('2. Presenting Overview & Architecture...');
  await smoothMouseMove(page, 200, 150, 20);
  await new Promise(r => setTimeout(r, 1200));

  await moveAndHover(page, '.hero-eyebrow', 15);
  await new Promise(r => setTimeout(r, 800));

  await moveAndHover(page, '.hero-title', 20);
  await new Promise(r => setTimeout(r, 1000));

  await moveAndHover(page, '.hero-stats-row', 25);
  await new Promise(r => setTimeout(r, 1500));

  // 0:08 - 0:17 (9s) Drag & drop file upload
  console.log('3. Interacting with Dropzone & Uploading ZIP...');
  await moveAndHover(page, '.upload-drop-zone', 25);
  await new Promise(r => setTimeout(r, 1000));

  const sampleZipPath = path.resolve('C:\\Users\\Thoufeek\\Desktop\\SSDLC Analyzer\\Demo_FinTech_Portal.zip');
  console.log(`Setting input file to: ${sampleZipPath}`);
  
  const fileInput = await page.$('input[type="file"]');
  await fileInput.setInputFiles(sampleZipPath);

  await new Promise(r => setTimeout(r, 1500));
  await moveAndHover(page, '.file-selected-state', 20);
  await new Promise(r => setTimeout(r, 1500));

  // 0:17 - 0:21 (4s) Trigger Security Analysis
  console.log('4. Starting Security Analysis...');
  await moveAndHover(page, '.start-scan-panel-btn', 20);
  await new Promise(r => setTimeout(r, 800));
  await page.click('.start-scan-panel-btn');

  // 0:21 - 0:34 (13s) Dedicated Scanning View Console
  console.log('5. Dedicated Security Scanning Console in progress...');
  await page.waitForSelector('.scanning-view-wrapper', { timeout: 10000 });
  await injectVirtualCursor(page);
  
  await moveAndHover(page, '.scanning-spinner-badge', 20);
  await new Promise(r => setTimeout(r, 2000));

  await moveAndHover(page, '.scanning-stats-grid', 25);
  await new Promise(r => setTimeout(r, 3000));

  await moveAndHover(page, '.scanning-phases-list', 25);
  
  console.log('Waiting for scanning console phases and backend analysis to complete...');
  await page.waitForSelector('.results-view-wrapper', { timeout: 60000 });
  console.log('Scan completed successfully! Results view visible.');
  await new Promise(r => setTimeout(r, 1500));
  await injectVirtualCursor(page);

  // 0:34 - 0:44 (10s) Results View & Score Reveal
  console.log('6. Inspecting Assessment Results & Score Posture...');
  await smoothMouseMove(page, 300, 200, 20);
  await new Promise(r => setTimeout(r, 1500));

  await moveAndHover(page, '.score-card-primary', 20);
  await new Promise(r => setTimeout(r, 2500));

  await moveAndHover(page, '.metric-card-item:nth-child(2)', 20);
  await new Promise(r => setTimeout(r, 1500));

  await moveAndHover(page, '.metric-card-item:nth-child(3)', 20);
  await new Promise(r => setTimeout(r, 1500));

  // 0:44 - 0:51 (7s) Domain Performance Assessment
  console.log('7. Reviewing SSDLC Domain Performance Cards...');
  await smoothScroll(page, 450, 1000);
  await new Promise(r => setTimeout(r, 800));

  await moveAndHover(page, '.domain-cards-grid .domain-performance-card:nth-child(1)', 20);
  await new Promise(r => setTimeout(r, 1200));

  await moveAndHover(page, '.domain-cards-grid .domain-performance-card:nth-child(2)', 20);
  await new Promise(r => setTimeout(r, 1200));

  await moveAndHover(page, '.domain-cards-grid .domain-performance-card:nth-child(3)', 20);
  await new Promise(r => setTimeout(r, 1200));

  // 0:51 - 1:02 (11s) Detailed Findings & Side Inspection Drawer
  console.log('8. Opening Detailed Finding Inspection Drawer...');
  await smoothScroll(page, 950, 1000);
  await new Promise(r => setTimeout(r, 800));

  const findingRows = await page.$$('.finding-row.clickable');
  if (findingRows.length > 0) {
    await moveAndHover(page, '.finding-row.clickable:nth-child(1)', 20);
    await new Promise(r => setTimeout(r, 800));
    await page.click('.finding-row.clickable:nth-child(1)');
    
    console.log('Side drawer opened. Inspecting technical evidence...');
    await page.waitForSelector('.drawer-container', { state: 'visible', timeout: 5000 });
    await new Promise(r => setTimeout(r, 1500));

    // Smooth hover inside the drawer
    await smoothMouseMove(page, 1000, 300, 20);
    await new Promise(r => setTimeout(r, 1500));

    const copyBtn = await page.$('.remediation-copy-btn');
    if (copyBtn) {
      await copyBtn.scrollIntoViewIfNeeded();
      await new Promise(r => setTimeout(r, 600));
      await page.click('.remediation-copy-btn');
      console.log('Remediation guidance copied!');
      await new Promise(r => setTimeout(r, 1500));
    }

    console.log('Closing drawer via Escape key...');
    await page.keyboard.press('Escape');
    await new Promise(r => setTimeout(r, 1200));
  }

  // 1:02 - 1:12 (10s) Download Security Assessment Report
  console.log('9. Downloading Security Assessment Report (PDF)...');
  await smoothScroll(page, 0, 1200);
  await new Promise(r => setTimeout(r, 1200));

  await moveAndHover(page, '.download-report-btn', 25);
  await new Promise(r => setTimeout(r, 1000));

  const downloadPromise = page.waitForEvent('download', { timeout: 20000 }).catch(() => null);
  await page.click('.download-report-btn');
  
  const download = await downloadPromise;
  if (download) {
    const suggestedFilename = download.suggestedFilename();
    const downloadDest = path.join(captureDir, suggestedFilename);
    await download.saveAs(downloadDest);
    console.log(`Report successfully downloaded to: ${downloadDest}`);
  }

  // Final hold on results view
  console.log('10. Final hold on completed assessment view...');
  await new Promise(r => setTimeout(r, 4000));

  console.log('Finishing and closing video recording context...');
  const video = page.video();
  await page.close();
  await context.close();
  await browser.close();

  const originalVideoPath = await video.path();
  console.log(`Playwright video recorded to: ${originalVideoPath}`);

  const finalWebmPath = path.join(captureDir, 'SSDLC_Analyzer_Demo.webm');
  const finalMp4Path = path.join(captureDir, 'SSDLC_Analyzer_Demo.mp4');

  fs.copyFileSync(originalVideoPath, finalWebmPath);
  console.log(`Saved demonstration video to: ${finalWebmPath}`);

  const ffmpegExe = 'C:\\Users\\Thoufeek\\AppData\\Local\\ms-playwright\\ffmpeg-1013\\ffmpeg-win64.exe';
  if (fs.existsSync(ffmpegExe)) {
    console.log('Transcoding to MP4 (H.264/AAC for universal Windows playback)...');
    try {
      execSync(`"${ffmpegExe}" -y -i "${finalWebmPath}" -c:v libx264 -pix_fmt yuv420p -r 30 "${finalMp4Path}"`, { stdio: 'inherit' });
      console.log(`Saved MP4 video to: ${finalMp4Path}`);
    } catch (e) {
      console.warn('MP4 conversion note:', e.message);
    }
  }

  console.log('--- Demonstration Recording Completed Successfully ---');
}

runDemo().catch(err => {
  console.error('Fatal error in runDemo:', err);
  process.exit(1);
});
