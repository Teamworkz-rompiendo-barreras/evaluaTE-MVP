// backend/index.ts
import express, { Request, Response } from 'express'
import path from 'path'
import fs from 'fs'
import puppeteer from 'puppeteer'

// 1) Crear la app de Express

const app = express()

app.use(express.json())
// Servir carpeta de plantillas (HTML y assets)
app.use(express.static(path.join(__dirname, '../templates')))

// 2) Endpoint para generar el informe en PDF
app.post('/api/generate-report', async (req: Request, res: Response) => {
  const { gameData, cvAnalysis } = req.body

  // Cargar plantilla HTML
  const templatePath = path.join(__dirname, '../templates/report.html')
  let html = fs.readFileSync(templatePath, 'utf8')

  // Inyectar datos en la plantilla
  const dataScript = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`
  html = html.replace('<!--__DATA_INJECTION__-->', dataScript)

  // Renderizar con Puppeteer
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] })
  const page = await browser.newPage()
  await page.setContent(html, { waitUntil: 'networkidle0' })
  const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true })
  await browser.close()

  // Enviar PDF al cliente
  res
    .status(200)
    .header('Content-Type', 'application/pdf')
    .header('Content-Disposition', 'attachment; filename="informe-resultados.pdf"')
    .send(pdfBuffer)
})

// 3) Arrancar el servidor y exportar la instancia para tests
const PORT = process.env.PORT || 3001
const server = app.listen(PORT, () => {
  console.log(`PDF report server running on port ${PORT}`)
})

export default server
