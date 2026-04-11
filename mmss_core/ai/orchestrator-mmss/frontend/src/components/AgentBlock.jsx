import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Loader2, CheckCircle, Circle } from 'lucide-react';
import MetricsDisplay from './MetricsDisplay';
import { MMSS_SYSTEM } from '../utils/mmss-system';

const AgentBlock = ({ agentType, status, result }) => {
  const config = MMSS_SYSTEM.AGENT_CONFIGURATIONS[agentType];
  const operator = MMSS_SYSTEM.QUANTUM_SEMANTIC_OPERATORS[config.operator];

  const statusConfig = {
    ready: { icon: Circle, color: '#4fc3f7', label: 'Ready' },
    running: { icon: Loader2, color: '#ff6b35', label: 'Running' },
    completed: { icon: CheckCircle, color: '#00d4aa', label: 'Completed' }
  };

  const currentStatus = statusConfig[status] || statusConfig.ready;
  const StatusIcon = currentStatus.icon;

  return (
    <Card className="agent-block">
      <CardHeader className="agent-header">
        <div className="agent-title-row">
          <div className="agent-operator-symbol" style={{ color: currentStatus.color }}>
            {operator.symbol}
          </div>
          <div className="agent-title-content">
            <CardTitle className="agent-title">{agentType.replace(/_/g, ' ')}</CardTitle>
            <div className="agent-quantum-state">{operator.quantum_state}</div>
          </div>
        </div>
        <Badge 
          variant="outline" 
          className="agent-status-badge"
          style={{ borderColor: currentStatus.color, color: currentStatus.color }}
        >
          <StatusIcon 
            size={14} 
            className={status === 'running' ? 'animate-spin' : ''} 
            style={{ marginRight: '4px' }}
          />
          {currentStatus.label}
        </Badge>
      </CardHeader>
      
      <CardContent className="agent-content">
        <div className="agent-purpose">
          <strong>Purpose:</strong> {config.purpose}
        </div>
        
        <div className="agent-thinking">
          <strong>Thinking Style:</strong> {config.thinking_style}
        </div>

        <div className="agent-formula">
          <strong>Formula:</strong>
          <code>{operator.formula}</code>
        </div>

        {status === 'completed' && result && (
          <>
            <div className="agent-answer">
              <strong>Answer:</strong>
              <div className="answer-text">{result.answer}</div>
            </div>
            
            {result.metrics && (
              <div className="agent-metrics">
                <strong>MMSS Metrics:</strong>
                <MetricsDisplay metrics={result.metrics} />
              </div>
            )}
          </>
        )}

        {status === 'running' && (
          <div className="agent-processing">
            <div className="processing-animation">
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
            </div>
            <p>Processing quantum transformation...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AgentBlock;