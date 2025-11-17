import React, { useState } from 'react';
import './App.css';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Progress } from './components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Switch } from './components/ui/switch';
import { Label } from './components/ui/label';
import { Download, Play } from 'lucide-react';
import AgentBlock from './components/AgentBlock';
import { MMSS_SYSTEM, MOCK_AGENT_RESPONSES } from './utils/mmss-system';
import { toast } from 'sonner';
import { Toaster } from './components/ui/sonner';

const AGENT_TYPES = [
  'QUANTUM_MAP',
  'META_DERIVATION',
  'FRACTAL_ENTAILMENT',
  'TEMPORAL_GENERATION',
  'GOLDEN_DERIVATION',
  'CORRECTION_ENHANCED'
];

function App() {
  const [question, setQuestion] = useState('');
  const [demoMode, setDemoMode] = useState(true);
  const [mistralKey, setMistralKey] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [agentStatuses, setAgentStatuses] = useState(
    AGENT_TYPES.reduce((acc, type) => ({ ...acc, [type]: 'ready' }), {})
  );
  const [agentResults, setAgentResults] = useState({});

  const executeAgent = async (agentType, questionText) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (demoMode) {
          const mockResponse = MOCK_AGENT_RESPONSES[agentType](questionText);
          resolve(mockResponse);
        } else {
          // TODO: Implement Mistral API call
          resolve({
            answer: 'Mistral API integration pending...',
            metrics: {
              V: 0.95,
              N: 0.94,
              S: 0.03,
              D_f: 9.0,
              G_S: 140,
              R_T: 2.618
            }
          });
        }
      }, 2000 + Math.random() * 1000);
    });
  };

  const startOrchestration = async () => {
    if (!question.trim()) {
      toast.error('Пожалуйста, введите вопрос');
      return;
    }

    if (!demoMode && !mistralKey.trim()) {
      toast.error('Пожалуйста, введите Mistral API ключ или включите Demo Mode');
      return;
    }

    setIsRunning(true);
    setProgress(0);
    setAgentStatuses(AGENT_TYPES.reduce((acc, type) => ({ ...acc, [type]: 'ready' }), {}));
    setAgentResults({});

    const results = {};

    for (let i = 0; i < AGENT_TYPES.length; i++) {
      const agentType = AGENT_TYPES[i];
      
      setAgentStatuses(prev => ({ ...prev, [agentType]: 'running' }));
      
      const result = await executeAgent(agentType, question);
      results[agentType] = result;
      
      setAgentResults(prev => ({ ...prev, [agentType]: result }));
      setAgentStatuses(prev => ({ ...prev, [agentType]: 'completed' }));
      
      const newProgress = ((i + 1) / AGENT_TYPES.length) * 100;
      setProgress(newProgress);
    }

    setIsRunning(false);
    
    const sessionData = {
      question,
      timestamp: new Date().toISOString(),
      mode: demoMode ? 'demo' : 'live',
      results
    };
    
    localStorage.setItem('mmss_last_results', JSON.stringify(sessionData));
    
    toast.success('Оркестрация завершена успешно!');
  };

  const downloadResults = () => {
    const sessionData = localStorage.getItem('mmss_last_results');
    if (!sessionData) {
      toast.error('Нет результатов для скачивания');
      return;
    }

    const blob = new Blob([sessionData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mmss-results-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('Результаты скачаны');
  };

  return (
    <div className="App">
      <Toaster />
      
      <div className="orchestrator-container">
        <Card className="control-panel">
          <CardHeader>
            <CardTitle className="panel-title">
              <span className="mmss-logo">MMSS</span>
              Orchestrator with Generative Relations
            </CardTitle>
            <div className="system-info">
              System ID: {MMSS_SYSTEM.SYSTEM_ACTIVATION.system_id}
            </div>
          </CardHeader>
          
          <CardContent>
            <div className="progress-section">
              <div className="progress-label">
                Progress: {Math.round(progress)}% 
                ({Object.values(agentStatuses).filter(s => s === 'completed').length}/{AGENT_TYPES.length} completed)
              </div>
              <Progress value={progress} className="progress-bar" />
            </div>

            <div className="question-section">
              <Label htmlFor="question" className="section-label">Question Input</Label>
              <Input
                id="question"
                placeholder="Enter your complex problem or question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={isRunning}
                className="question-input"
              />
            </div>

            <div className="mode-section">
              <div className="mode-toggle">
                <Switch
                  id="demo-mode"
                  checked={demoMode}
                  onCheckedChange={setDemoMode}
                  disabled={isRunning}
                />
                <Label htmlFor="demo-mode" className="mode-label">
                  Demo Mode (Mock Responses)
                </Label>
              </div>

              {!demoMode && (
                <div className="api-key-section">
                  <Label htmlFor="mistral-key" className="section-label">Mistral API Key</Label>
                  <Input
                    id="mistral-key"
                    type="password"
                    placeholder="Enter Mistral API key..."
                    value={mistralKey}
                    onChange={(e) => setMistralKey(e.target.value)}
                    disabled={isRunning}
                    className="api-key-input"
                  />
                </div>
              )}
            </div>

            <div className="action-buttons">
              <Button
                onClick={startOrchestration}
                disabled={isRunning}
                className="start-button"
                size="lg"
              >
                {isRunning ? (
                  <>
                    <span className="button-spinner"></span>
                    Running...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    Start Orchestration
                  </>
                )}
              </Button>

              <Button
                onClick={downloadResults}
                variant="outline"
                className="download-button"
                size="lg"
                disabled={Object.keys(agentResults).length === 0}
              >
                <Download size={18} />
                Download Results
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="agents-grid">
          {AGENT_TYPES.map((agentType) => (
            <AgentBlock
              key={agentType}
              agentType={agentType}
              status={agentStatuses[agentType]}
              result={agentResults[agentType]}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;