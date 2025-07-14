// backend/index.ts
import app from './src/app';

// Arrancar el servidor solo si este archivo es ejecutado directamente
if (require.main === module) {
  const PORT = process.env.PORT || 8080;
  app.listen(PORT, () => {
    console.log(`EvaluaTE backend server running on port ${PORT}`);
  });
}

export default app;
