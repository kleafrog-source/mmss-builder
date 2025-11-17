import React from 'react';
import { Activity, TrendingUp, AlertCircle, Layers, Zap, Star } from 'lucide-react';
import { METRICS_VALIDATION } from '../utils/mmss-system';

const MetricsDisplay = ({ metrics }) => {
  const getMetricStatus = (key, value) => {
    const validation = METRICS_VALIDATION[key];
    if (!validation) return 'neutral';
    
    if (key === 'S') {
      return value <= validation.optimal * 1.5 ? 'success' : 'warning';
    }
    
    const deviation = Math.abs(value - validation.optimal);
    const tolerance = (validation.max - validation.min) * 0.1;
    
    if (deviation <= tolerance) return 'success';
    if (deviation <= tolerance * 2) return 'warning';
    return 'error';
  };

  const metricIcons = {
    V: Activity,
    N: TrendingUp,
    S: AlertCircle,
    D_f: Layers,
    G_S: Zap,
    R_T: Star
  };

  const statusColors = {
    success: '#00d4aa',
    warning: '#ff6b35',
    error: '#ff4757',
    neutral: '#4fc3f7'
  };

  return (
    <div className="metrics-grid">
      {Object.entries(metrics).map(([key, value]) => {
        const Icon = metricIcons[key] || Activity;
        const status = getMetricStatus(key, value);
        const color = statusColors[status];
        const validation = METRICS_VALIDATION[key];

        return (
          <div key={key} className="metric-item" style={{ borderLeftColor: color }}>
            <div className="metric-header">
              <Icon size={16} style={{ color }} />
              <span className="metric-key">{key}</span>
            </div>
            <div className="metric-value" style={{ color }}>
              {typeof value === 'number' ? value.toFixed(4) : value}
            </div>
            {validation && (
              <div className="metric-label">{validation.name}</div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default MetricsDisplay;