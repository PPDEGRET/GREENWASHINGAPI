# LeafCheck Web

This directory contains the static landing page for LeafCheck.

## Local Preview

To preview the website locally, you can use any simple HTTP server. If you have Node.js installed, you can use the `serve` package:

```bash
npx serve web
```

Alternatively, if you are using Visual Studio Code, you can use the "Live Server" extension.

## Changing the Streamlit App URL

The "Open the App" button points to a URL defined in `web/main.js`. To change this URL, open the file and modify the `APP_URL` constant:

```javascript
const APP_URL = "http://localhost:8501"; // Change this to your app's URL
```
