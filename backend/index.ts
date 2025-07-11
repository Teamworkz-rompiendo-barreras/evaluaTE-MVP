// backend/index.ts
import express, { Request, Response } from 'express'
import path from 'path'
import fs from 'fs'
import puppeteer from 'puppeteer'
import iaReportRoute from './src/routes/iaReportRoute';
import cors from 'cors'

const app = express()
app.use(cors({
  origin: 'http://localhost:3005',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  credentials: true // Permite el envío de cookies/autenticación si es necesario
}))
app.use(express.json())
app.use(express.static(path.join(__dirname, '../templates')))
app.use('/api/informe-ia', iaReportRoute);

app.post('/api/generate-report', async (req: Request, res: Response) => {
  const { gameData, cvAnalysis } = req.body
  const templatePath = path.join(__dirname, '../templates/report.html')
  let html = fs.readFileSync(templatePath, 'utf8')
  const dataScript = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`
  html = html.replace('<!--__DATA_INJECTION__-->', dataScript)
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] })
  const page = await browser.newPage()
  await page.setContent(html, { waitUntil: 'networkidle0' })
  const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true })
  await browser.close()
  res
    .status(200)
    .header('Content-Type', 'application/pdf')
    .header('Content-Disposition', 'attachment; filename=\"informe-resultados.pdf\"')
    .send(pdfBuffer)
})

// Solo arrancar el server si este archivo es ejecutado directamente (no en test)
if (require.main === module) {
  const PORT = process.env.PORT || 3001
  app.listen(PORT, () => {
    console.log(`PDF report server running on port ${PORT}`)
  })
}

// Exporta la app de Express para los tests
export default app
