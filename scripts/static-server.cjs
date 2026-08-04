const http = require('http')
const fs = require('fs')
const path = require('path')

const root = path.resolve(process.cwd())
const port = Number(process.argv[2] || process.env.PORT || 4173)

const mimeTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
}

http.createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
  let filePath = path.resolve(root, `.${pathname}`)

  if (!filePath.startsWith(root + path.sep) && filePath !== root) {
    response.writeHead(403).end('Forbidden')
    return
  }

  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, 'index.html')
  }

  fs.readFile(filePath, (error, content) => {
    if (error) {
      response.writeHead(error.code === 'ENOENT' ? 404 : 500).end('Not found')
      return
    }
    response.writeHead(200, { 'Content-Type': mimeTypes[path.extname(filePath)] || 'application/octet-stream' })
    response.end(content)
  })
}).listen(port, '127.0.0.1', () => {
  console.log(`Static server: http://127.0.0.1:${port}`)
})
