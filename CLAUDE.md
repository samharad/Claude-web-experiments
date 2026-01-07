# Tools

## Overview / Spec

'Tools' here refers to small, AI-coded, bespoke tools made by me (Sam) and kept in my `tools` github repo.

Most tools are 'webtools', which are kept under the `/web/` directory, implemented using web technology (HTML, CSS, JavaScript, etc.), and hosted at `tools.samadams.dev`.

A webtool gets its own directory under `/web/`, e.g. `/web/<tool-name>/`. Usually and by default, this directory should contain just two files: an `index.html` file and a `README.md` file. (During tool development, if the tool proves to be complicated and requires a more complex structure, then we may deviate from this.)

The `index.html` file contains the entire webtool implementation, with any necessary CSS and JavaScript inline. 

The `README.md` file contains a description / specification of the tool and its intent / purpose. 

The root of the repo should itself contain an `index.html` file which describes and links to the various webtools.

## Additional guidance

- DO NOT use React! 
- If JavaScript dependencies are absolutely necessary, load them from a CDN





