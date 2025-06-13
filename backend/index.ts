// backend/index.ts
import express from 'express'
import path from 'path'
import fs from 'fs'
import puppeteer from 'puppeteer'

const app = express()
app.use(express.json())
// Sirve los archivos estáticos de templates (si quieres exponer report.html o assets)
app.use(express.static(path.join(__dirname, '../templates')))

app.post('/api/generate-report', async (req, res) => {
  const { gameData, cvAnalysis } = req.body
  const templatePath = path.join(__dirname, '../templates/report.html')
  let html = fs.readFileSync(templatePath, 'utf8')
  const injection = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`
  html = html.replace('<!--__DATA_INJECTION__-->', injection)

  const browser = await puppeteer.launch({ args: ['--no-sandbox'] })
  const page = await browser.newPage()
  await page.setContent(html, { waitUntil: 'networkidle0' })
  const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true })
  await browser.close()

  res
    .status(200)
    .set({
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="informe-resultados.pdf"',
    })
    .send(pdfBuffer)
})

const PORT = process.env.PORT || 3001
app.listen(PORT, () => console.log(`PDF report server running on port ${PORT}`))
