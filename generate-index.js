#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Read all directories in web/
const webDir = path.join(__dirname, 'web');
const dirs = fs.readdirSync(webDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)
    .sort();

// Extract title, description, and last-modified date from each tool's index.html
const tools = [];

for (const dir of dirs) {
    const indexPath = path.join(webDir, dir, 'index.html');

    if (!fs.existsSync(indexPath)) {
        console.warn(`Warning: ${dir} has no index.html, skipping`);
        continue;
    }

    const html = fs.readFileSync(indexPath, 'utf8');

    // Extract title
    const titleMatch = html.match(/<title>(.*?)<\/title>/i);
    const title = titleMatch ? titleMatch[1] : dir;

    // Extract meta description
    const descMatch = html.match(/<meta\s+name=["']description["']\s+content=["'](.*?)["']/i);
    const description = descMatch ? descMatch[1] : '';

    // Get last git commit date for this tool directory
    let modifiedISO = '';
    try {
        modifiedISO = execSync(`git log -1 --format='%aI' -- "web/${dir}"`, { cwd: __dirname, encoding: 'utf8' }).trim();
    } catch (e) {
        // fallback below
    }

    // A brand-new tool has no git history yet when the pre-commit hook
    // runs, which would leave it undated and sorted last under
    // "Recently modified" — fall back to the file's mtime
    if (!modifiedISO) {
        modifiedISO = fs.statSync(indexPath).mtime.toISOString();
    }

    tools.push({
        dir,
        title,
        description,
        url: `web/${dir}/`,
        modified: modifiedISO
    });
}

const buildTimestamp = new Date();
const buildTimestampFormatted = buildTimestamp
    .toISOString()
    .replace('T', ' ')
    .replace(/\.\d{3}Z$/, ' UTC');

function renderTool(tool) {
    const desc = tool.description ? `\n            <div class="description">${tool.description}</div>` : '';
    const modified = tool.modified ? `\n            <div class="modified" data-sort="recent">Modified: ${new Date(tool.modified).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</div>` : '';
    return `        <li data-alpha="${tool.title.toLowerCase()}" data-modified="${tool.modified || ''}">
            <a href="${tool.url}">${tool.title}</a>${desc}${modified}
        </li>`;
}

// Generate index.html
const indexHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tools</title>
    <style>
        :root {
            --bg: #fff;
            --fg: #000;
            --muted: #666;
            --faint: #999;
            --link: #0066cc;
            --border: #ddd;
        }
        html.night {
            --bg: #1a1a2e;
            --fg: #e0e0e0;
            --muted: #aaa;
            --faint: #777;
            --link: #5ba3f5;
            --border: #333;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            line-height: 1.6;
            background: var(--bg);
            color: var(--fg);
            transition: background 0.2s, color 0.2s;
        }
        h1 {
            margin-bottom: 2rem;
        }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        .top-bar h1 {
            margin: 0;
        }
        .night-toggle {
            background: none;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.3rem 0.6rem;
            cursor: pointer;
            font-size: 1.2rem;
            line-height: 1;
            color: var(--fg);
            transition: border-color 0.2s;
        }
        .night-toggle:hover {
            border-color: var(--muted);
        }
        .deploy-time {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: -1.5rem;
            margin-bottom: 2rem;
        }
        .sort-controls {
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        .sort-controls label {
            cursor: pointer;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .sort-controls span {
            color: var(--muted);
            font-size: 0.9rem;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 1rem 0;
        }
        a {
            color: var(--link);
            text-decoration: none;
            font-weight: 600;
        }
        a:hover {
            text-decoration: underline;
        }
        .description {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        .modified {
            color: var(--faint);
            font-size: 0.8rem;
            margin-top: 0.15rem;
            display: none;
        }
    </style>
</head>
<body>
    <div class="top-bar">
        <h1>Tools</h1>
        <button class="night-toggle" id="night-toggle" title="Toggle night mode">🌙</button>
    </div>
    <div class="deploy-time">Deployed: ${buildTimestampFormatted}</div>
    <div class="sort-controls">
        <span>Sort by:</span>
        <label><input type="radio" name="sort" value="alpha" checked> Alphabetical</label>
        <label><input type="radio" name="sort" value="recent"> Recently modified</label>
    </div>
    <ul id="tool-list">
${tools.map(renderTool).join('\n')}
    </ul>
    <script>
        const list = document.getElementById('tool-list');
        const radios = document.querySelectorAll('input[name="sort"]');
        const modifiedDivs = document.querySelectorAll('.modified');

        function sortList(order) {
            const items = Array.from(list.children);
            items.sort((a, b) => {
                if (order === 'recent') {
                    const am = a.dataset.modified || '';
                    const bm = b.dataset.modified || '';
                    return bm.localeCompare(am);
                }
                return a.dataset.alpha.localeCompare(b.dataset.alpha);
            });
            items.forEach(item => list.appendChild(item));
            modifiedDivs.forEach(el => el.style.display = order === 'recent' ? 'block' : 'none');
        }

        radios.forEach(radio => radio.addEventListener('change', () => {
            localStorage.setItem('tools-sort', radio.value);
            sortList(radio.value);
        }));

        const saved = localStorage.getItem('tools-sort');
        if (saved) {
            const target = document.querySelector('input[name="sort"][value="' + saved + '"]');
            if (target) {
                target.checked = true;
                sortList(saved);
            }
        }

        const nightBtn = document.getElementById('night-toggle');
        function applyNight(on) {
            document.documentElement.classList.toggle('night', on);
            nightBtn.textContent = on ? '☀️' : '🌙';
        }
        applyNight(localStorage.getItem('tools-night') === '1');
        nightBtn.addEventListener('click', () => {
            const on = !document.documentElement.classList.contains('night');
            localStorage.setItem('tools-night', on ? '1' : '0');
            applyNight(on);
        });
    </script>
</body>
</html>
`;

fs.writeFileSync(path.join(__dirname, 'index.html'), indexHtml);
console.log('Generated index.html');
