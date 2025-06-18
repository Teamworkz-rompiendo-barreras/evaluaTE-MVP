// backend/index.ts
import express, { Request, Response } from 'express'
import path from 'path'
import fs from 'fs'
import puppeteer from 'puppeteer'

// 2) Declaración de la app, justo aquí
const app = express()

// Creamos la aplicación de Express\ nconst app = express()
app.use(express.json())
// Servimos la carpeta de plantillas (HTML y assets)
app.use(express.static(path.join(__dirname, '../templates')))

// Endpoint para generar el informe en PDF
app.post('/api/generate-report', async (req: Request, res: Response) => {
  const { gameData, cvAnalysis } = req.body

  // Cargamos la plantilla HTML
  const templatePath = path.join(__dirname, '../templates/report.html')
  let html = fs.readFileSync(templatePath, 'utf8')

  // Inyectamos los datos en la plantilla
  const dataScript = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`
  html = html.replace('<!--__DATA_INJECTION__-->', dataScript)

  // Lanzamos Puppeteer para renderizar el HTML y generar el PDF
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] })
  const page = await browser.newPage()
  await page.setContent(html, { waitUntil: 'networkidle0' })
  const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true })
  await browser.close()

  // Enviamos el PDF generado al cliente
  res
    .status(200)
    .header('Content-Type', 'application/pdf')
    .header('Content-Disposition', 'attachment; filename="informe-resultados.pdf"')
    .send(pdfBuffer)
})

// Arrancamos el servidor y exportamos la instancia para los tests
const PORT = process.env.PORT || 3001
const server = app.listen(PORT, () => {
  console.log(`PDF report server running on port ${PORT}`)
})

export default server
