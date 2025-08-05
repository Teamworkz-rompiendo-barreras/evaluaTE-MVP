import React, { useState, useEffect } from 'react';
import { buildApiUrl } from '../config/api';

interface FeedbackItem {
  informe: string;
  rating: string;
  comment: string;
  userData: {
    minigames?: Array<unknown>;
    preferences?: {
      areas?: string[];
    };
  };
  timestamp: string;
}

interface FeedbackStats {
  total_feedback: number;
  useful_feedback: number;
  not_useful_feedback: number;
  useful_percentage: number;
  recent_feedback: FeedbackItem[];
  common_comments: string[];
}

const FeedbackDashboard: React.FC = () => {
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null);

  const fetchFeedbackStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(buildApiUrl('/api/informe-ia/feedback/stats'));
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        setError('Error al cargar las estadísticas');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedbackStats();
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchFeedbackStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('es-ES');
  };

  const getRatingColor = (rating: string) => {
    return rating === 'Útil' ? 'text-green-600' : 'text-red-600';
  };

  const getRatingIcon = (rating: string) => {
    return rating === 'Útil' ? '👍' : '👎';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-32 bg-gray-300 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard de Feedback IA
          </h1>
          <p className="text-gray-600">
            Monitoreo en tiempo real del feedback de usuarios sobre los informes de IA
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Feedback</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_feedback || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <span className="text-2xl">👍</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Útil</p>
                <p className="text-2xl font-bold text-green-600">{stats?.useful_feedback || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <span className="text-2xl">👎</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">No Útil</p>
                <p className="text-2xl font-bold text-red-600">{stats?.not_useful_feedback || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <span className="text-2xl">📈</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">% Satisfacción</p>
                <p className="text-2xl font-bold text-purple-600">{stats?.useful_percentage || 0}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Feedback */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Feedback List */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Feedback Reciente</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {stats?.recent_feedback.map((feedback, index) => (
                <div
                  key={index}
                  className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setSelectedFeedback(feedback)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`font-medium ${getRatingColor(feedback.rating)}`}>
                      {getRatingIcon(feedback.rating)} {feedback.rating}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatDate(feedback.timestamp)}
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm line-clamp-2">
                    {feedback.comment || 'Sin comentarios'}
                  </p>
                  {feedback.userData?.minigames && (
                    <p className="text-xs text-gray-500 mt-2">
                      {feedback.userData.minigames.length} habilidades evaluadas
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Feedback Detail */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Detalle del Feedback</h2>
            </div>
            <div className="p-6">
              {selectedFeedback ? (
                <div>
                  <div className="mb-4">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRatingColor(selectedFeedback.rating)} bg-gray-100`}>
                      {getRatingIcon(selectedFeedback.rating)} {selectedFeedback.rating}
                    </span>
                    <span className="ml-2 text-sm text-gray-500">
                      {formatDate(selectedFeedback.timestamp)}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <h3 className="font-medium text-gray-900 mb-2">Comentario:</h3>
                    <p className="text-gray-700 bg-gray-50 p-3 rounded">
                      {selectedFeedback.comment || 'Sin comentarios'}
                    </p>
                  </div>

                  {selectedFeedback.userData && (
                    <div className="mb-4">
                      <h3 className="font-medium text-gray-900 mb-2">Datos del Usuario:</h3>
                      <div className="bg-gray-50 p-3 rounded text-sm">
                        <p><strong>Habilidades evaluadas:</strong> {selectedFeedback.userData.minigames?.length || 0}</p>
                        {selectedFeedback.userData.preferences?.areas && (
                          <p><strong>Áreas de interés:</strong> {selectedFeedback.userData.preferences.areas.join(', ')}</p>
                        )}
                      </div>
                    </div>
                  )}

                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Informe Generado:</h3>
                    <div className="bg-gray-50 p-3 rounded max-h-64 overflow-y-auto text-sm">
                      <pre className="whitespace-pre-wrap text-gray-700">
                        {selectedFeedback.informe.substring(0, 500)}...
                      </pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  Selecciona un feedback para ver los detalles
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Common Comments */}
        {stats?.common_comments && stats.common_comments.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Comentarios Frecuentes</h2>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {stats.common_comments.map((comment, index) => (
                  <div key={index} className="bg-gray-50 p-3 rounded">
                    <p className="text-gray-700">{comment}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Refresh Button */}
        <div className="mt-8 text-center">
          <button
            onClick={fetchFeedbackStats}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔄 Actualizar Datos
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackDashboard;