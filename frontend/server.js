const { createServer } = require('https');
const { parse } = require('url');
const next = require('next');
const fs = require('fs');
const path = require('path');
const http = require('http');

const dev = process.env.NODE_ENV !== 'production';
const hostname = '0.0.0.0';
const port = 3000;
const backendUrl = 'http://localhost:8000';

const app = next({ dev, hostname, port });
const handle = app.getRequestHandler();

const httpsOptions = {
  key: fs.readFileSync(path.join(__dirname, 'localhost+3-key.pem')),
  cert: fs.readFileSync(path.join(__dirname, 'localhost+3.pem')),
};

app.prepare().then(() => {
  createServer(httpsOptions, async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true);
      
      // Proxy /api requests to backend
      if (parsedUrl.pathname && parsedUrl.pathname.startsWith('/api')) {
        const targetPath = parsedUrl.pathname.replace(/^\/api/, '') + (parsedUrl.search || '');
        const targetUrl = backendUrl + targetPath;
        
        const proxyReq = http.request(
          targetUrl,
          {
            method: req.method,
            headers: {
              ...req.headers,
              host: 'localhost:8000',
            },
          },
          (proxyRes) => {
            res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
            proxyRes.pipe(res);
          }
        );
        
        proxyReq.on('error', (err) => {
          console.error('Proxy error:', err);
          res.statusCode = 502;
          res.end('Bad Gateway');
        });
        
        req.pipe(proxyReq);
        return;
      }
      
      await handle(req, res, parsedUrl);
    } catch (err) {
      console.error('Error occurred handling', req.url, err);
      res.statusCode = 500;
      res.end('internal server error');
    }
  })
    .once('error', (err) => {
      console.error(err);
      process.exit(1);
    })
    .listen(port, hostname, () => {
      console.log(`> Ready on https://${hostname}:${port}`);
      console.log(`> Local: https://localhost:${port}`);
      console.log(`> Network: https://172.20.10.3:${port}`);
      console.log(`> Proxying /api to ${backendUrl}`);
    });
});
