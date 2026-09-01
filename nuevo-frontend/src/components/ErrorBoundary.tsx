import React from 'react';
import * as Sentry from '@sentry/react';
import { reportError } from '../sentry';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    reportError(error, {
      errorInfo,
      componentStack: errorInfo.componentStack,
    });
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined });
  };

  override render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return (
        <FallbackComponent 
          error={this.state.error} 
          resetError={this.resetError} 
        />
      );
    }

    return this.props.children;
  }
}

const isChunkLoadError = (error?: Error): boolean => {
  if (!error) return false;
  return (
    error.message?.includes('Failed to fetch dynamically imported module') ||
    error.message?.includes('Importing a module script failed') ||
    error.name === 'ChunkLoadError'
  );
};

// Componente de fallback adaptado a WCAG 2.2 AA (Alertas y Contraste)
const DefaultErrorFallback: React.FC<{ error?: Error; resetError: () => void }> = ({
  error,
  resetError
}) => {
  const chunkError = isChunkLoadError(error);

  if (chunkError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
        <div 
          className="max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6 transition-colors text-center" 
          role="alert" 
          aria-live="assertive"
        >
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 mb-4" aria-hidden="true">
            <svg className="h-6 w-6 text-yellow-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <h3 className="text-base font-bold text-gray-900 dark:text-gray-100">Nueva versión disponible</h3>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            La plataforma ha recibido una actualización crítica. Por favor, recarga la página para aplicar los cambios.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 inline-flex items-center px-6 py-3 border border-transparent text-sm font-bold rounded-md shadow-sm text-white bg-blue-700 hover:bg-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-300 transition-colors"
          >
            Recargar plataforma
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
      <div 
        className="max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6 transition-colors"
        role="alert" 
        aria-live="assertive"
      >
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100" aria-hidden="true">
            <svg className="h-6 w-6 text-red-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="mt-4 text-base font-bold text-gray-900 dark:text-white">
            Interrupción en el procesamiento
          </h3>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Se ha producido una desincronización inesperada de datos. Nuestro equipo técnico ha sido notificado automáticamente.
          </p>
          
          {error && (
            <details className="mt-5 text-left bg-gray-50 dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700">
              <summary className="cursor-pointer text-sm font-bold text-gray-700 dark:text-gray-300 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-1">
                Ver diagnóstico técnico
              </summary>
              <pre className="mt-3 text-xs text-red-800 dark:text-red-300 whitespace-pre-wrap font-mono break-words">
                {error.message}
              </pre>
            </details>
          )}
          
          <div className="mt-6">
            <button
              onClick={resetError}
              className="inline-flex items-center px-6 py-3 border border-transparent text-sm font-bold rounded-md shadow-sm text-white bg-blue-700 hover:bg-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-300 transition-colors w-full justify-center"
            >
              Reintentar operación
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const withSentry = (Component: React.ComponentType<unknown>) => {
  return Sentry.withProfiler(Component);
};

export default ErrorBoundary;