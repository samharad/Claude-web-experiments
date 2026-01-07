#!/usr/bin/env node

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Generate HTML for a dial at a specific angle
function generateDialSVG(angle) {
    // Convert angle to radians for calculating endpoint
    const radians = (angle - 90) * Math.PI / 180;
    const armLength = 150;
    const centerX = 200;
    const centerY = 200;
    const endX = centerX + armLength * Math.cos(radians);
    const endY = centerY + armLength * Math.sin(radians);

    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 1200px;
            height: 630px;
        }
    </style>
</head>
<body>
    <svg width="800" height="426" viewBox="40 40 320 170">
        <!-- Dial base semicircle -->
        <path d="M 50 200 A 150 150 0 0 1 350 200 Z" fill="#ffffff" stroke="#cccccc" stroke-width="3"/>

        <!-- Center dot -->
        <circle cx="200" cy="200" r="10" fill="#660000"/>

        <!-- Dial arm -->
        <line x1="200" y1="200" x2="${endX}" y2="${endY}" stroke="#ff0000" stroke-width="8" stroke-linecap="round"/>
    </svg>
</body>
</html>`;
}

async function generatePreviews() {
    console.log('Launching browser...');
    const browser = await puppeteer.launch({
        headless: 'new',
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Set viewport to Open Graph recommended size (1200x630)
    await page.setViewport({
        width: 1200,
        height: 630,
        deviceScaleFactor: 2 // For retina quality
    });

    const previewsDir = path.join(__dirname, 'previews');
    if (!fs.existsSync(previewsDir)) {
        fs.mkdirSync(previewsDir, { recursive: true });
    }

    console.log('Generating preview images...');
    let count = 0;

    for (let angle = -90; angle <= 90; angle++) {
        const html = generateDialSVG(angle);
        await page.setContent(html);

        const angleStr = angle < 0 ? `minus${Math.abs(angle)}` : angle.toString();
        const filename = `dial-${angleStr}.png`;
        const filepath = path.join(previewsDir, filename);

        await page.screenshot({
            path: filepath,
            type: 'png'
        });

        count++;
        if (count % 20 === 0) {
            console.log(`Generated ${count}/181 images...`);
        }
    }

    await browser.close();
    console.log(`\nSuccessfully generated ${count} preview images in previews/`);
}

// Check if puppeteer is installed
try {
    require.resolve('puppeteer');
    generatePreviews().catch(err => {
        console.error('Error generating previews:', err);
        process.exit(1);
    });
} catch (e) {
    console.error('Puppeteer is not installed. Installing now...');
    console.log('Run: npm install puppeteer');
    console.log('Then run this script again: node generate-preview-images.js');
    process.exit(1);
}
