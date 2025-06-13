// src/pages/ResultadosPage.tsx
import React from 'react'
import { useAppSelector } from '../app/hooks'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'
import { Button } from '@/components/ui/button'

export default function ResultadosPage() {
  // Imagina que en el state tienes un objeto { skill: score } 
  const scores = useAppSelector(s => s.progress.scores)  
  // Ejemplo: { "Comunicación": 80, "Trabajo en equipo": 65, … }

  // Convertimos a array para Recharts
  const data = Object.entries(scores).map(([skill, value]) => ({
    subject: skill,
    A: value,
    fullMark: 100
  }))

  return (
    <main className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">¡Tu evaluación está lista!</h1>

      <section className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis angle={30} domain={[0,100]} />
            <Radar name="Tú" dataKey="A" stroke="#374BA6" fill="#374BA6" fillOpacity={0.6} />
          </RadarChart>
        </ResponsiveContainer>
      </section>

      <section className="mt-8 space-y-4">
        <h2 className="text-xl font-semibold">Puntos fuertes</h2>
        <ul className="list-disc pl-5">
          {data.filter(d => d.A >= 75).map(d =>
            <li key={d.subject}>{d.subject}: {d.A}%</li>
          )}
        </ul>

        <h2 className="text-xl font-semibold mt-6">Áreas a mejorar</h2>
        <ul className="list-disc pl-5">
          {data.filter(d => d.A < 75).map(d =>
            <li key={d.subject}>{d.subject}: {d.A}%</li>
          )}
        </ul>
      </section>

      <div className="mt-8 text-center">
        <Button onClick={() => window.print()}>Descargar PDF</Button>
      </div>
    </main>
  )
}
