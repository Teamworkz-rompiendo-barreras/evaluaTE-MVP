// backend/src/app.ts
import express from 'express';
import bodyParser from 'body-parser';
import pdfRoute from './routes/pdfRoute'; // Asegúrate de que la ruta sea correcta
import iaReportRoute from './routes/iaReportRoute';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(bodyParser.json());
app.use('/api', pdfRoute);
app.use('/api/informe-ia', iaReportRoute);

const server = app.listen(PORT, () => {
  console.log(`PDF report server running on port ${PORT}`);
});

export { app, server };