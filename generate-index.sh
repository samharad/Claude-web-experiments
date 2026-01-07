#!/bin/bash

# Generate root index.html linking to all webtools

cat > index.html << 'EOF'
<!DOCTYPE html>
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
            margin: 0.5rem 0;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Tools</h1>
    <ul>
EOF

# Find all directories in web/ and create links
for dir in web/*/; do
    if [ -d "$dir" ]; then
        # Extract directory name without web/ prefix and trailing slash
        name=$(basename "$dir")
        # Convert hyphens to spaces and capitalize for display
        display_name=$(echo "$name" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
        echo "        <li><a href=\"$dir\">$display_name</a></li>" >> index.html
    fi
done

cat >> index.html << 'EOF'
    </ul>
</body>
</html>
EOF

echo "Generated index.html"
