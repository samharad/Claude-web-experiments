#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Read all directories in web/
const webDir = path.join(__dirname, 'web');
const dirs = fs.readdirSync(webDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)
    .sort();

// Extract title and description from each tool's index.html
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

    tools.push({
        dir,
        title,
        description,
        url: `web/${dir}/`
    });
}

// Generate index.html
const indexHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tools</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            line-height: 1.6;
        }
        h1 {
            margin-bottom: 2rem;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 1rem 0;
        }
        a {
            color: #0066cc;
            text-decoration: none;
            font-weight: 600;
        }
        a:hover {
            text-decoration: underline;
        }
        .description {
            color: #666;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
    </style>
</head>
<body>
    <h1>Tools</h1>
    <ul>
${tools.map(tool => `        <li>
            <a href="${tool.url}">${tool.title}</a>${tool.description ? `\n            <div class="description">${tool.description}</div>` : ''}
        </li>`).join('\n')}
    </ul>
</body>
</html>
`;

fs.writeFileSync(path.join(__dirname, 'index.html'), indexHtml);
console.log('Generated index.html');
