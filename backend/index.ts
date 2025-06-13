/* File: server/index.ts */
import express from 'express'
import path from 'path'
import fs from 'fs'
import puppeteer from 'puppeteer'

const app = express()
app.use(express.json())

// Endpoint to generate PDF report
app.post('/api/generate-report', async (req, res) => {
  const { gameData, cvAnalysis } = req.body
  
  // 1️⃣ Load HTML template
  const templatePath = path.join(__dirname, '../templates/report.html')
  let html = fs.readFileSync(templatePath, 'utf8')

  // 2️⃣ Inject data into template
  const dataScript = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`
  html = html.replace('<!--__DATA_INJECTION__-->', dataScript)

  // 3️⃣ Launch headless browser and render PDF
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] })
  const page = await browser.newPage()
  await page.setContent(html, { waitUntil: 'networkidle0' })
  const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true })
  await browser.close()

  // 4️⃣ Send PDF to client
  res.set({
    'Content-Type': 'application/pdf',
    'Content-Disposition': 'attachment; filename="informe-resultados.pdf"',
  })
  res.send(pdfBuffer)
})

// Serve static assets (CSS, JS libs)
app.use(express.static(path.join(__dirname, '../templates')))

const PORT = process.env.PORT || 3001
app.listen(PORT, () => {
  console.log(`PDF report server running on port ${PORT}`)
})

/* File: templates/report.html */
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Informe de Resultados</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet" />
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!--__DATA_INJECTION__-->
</head>
<body class="p-8 bg-gray-50">
  <div class="max-w-2xl mx-auto bg-white p-6 rounded shadow">
    <h1 class="text-3xl font-bold mb-4 text-center">Informe de Resultados</h1>
    <section>
      <h2 class="text-2xl font-semibold mb-2">Análisis de tu CV</h2>
      <p><strong>Puntuación:</strong> <span id="score"></span>/100</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div>
          <h3 class="font-medium">Fortalezas</h3>
          <ul id="strengths" class="list-disc ml-6"></ul>
        </div>
        <div>
          <h3 class="font-medium">Áreas a mejorar</h3>
          <ul id="weaknesses" class="list-disc ml-6"></ul>
        </div>
      </div>
    </section>
    <section class="mt-8">
      <h2 class="text-2xl font-semibold mb-2">Minijuegos</h2>
      <canvas id="radarChart" width="400" height="400"></canvas>
    </section>
  </div>
  <script>
    ;(function() {
      const { gameData = [], cvAnalysis = {} } = window.__REPORT_DATA__ || {}
      // Populate CV data
      document.getElementById('score').textContent = cvAnalysis.score
      const strengthsEl = document.getElementById('strengths')
      cvAnalysis.strengths.forEach(s => {
        const li = document.createElement('li')
        li.textContent = s
        strengthsEl.appendChild(li)
      })
      const weaknessesEl = document.getElementById('weaknesses')
      cvAnalysis.weaknesses.forEach(w => {
        const li = document.createElement('li')
        li.textContent = w
        weaknessesEl.appendChild(li)
      })
      // Generate Radar Chart
      const labels = gameData.map(d => d.subject)
      const data = gameData.map(d => d.dA)
      new Chart(document.getElementById('radarChart'), {
        type: 'radar',
        data: {
          labels,
          datasets: [{ label: 'Resultados Minijuegos', data }]
        },
        options: {
          scale: { ticks: { beginAtZero: true, max: 100 } }
        }
      })
    })()
  </script>
</body>
</html>