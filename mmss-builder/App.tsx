import React, { useState } from 'react';
import { generateMMSS } from './services/aiService';
import { AppState, AIProvider, MMSSRoot } from './types';
import { EXAMPLE_INPUT } from './constants';
import NetworkVisualizer from './components/NetworkVisualizer';
import "tailwindcss";

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    inputText: EXAMPLE_INPUT,
    jsonOutput: null,
    isLoading: false,
    error: null,
    provider: AIProvider.GEMINI, // Default per system instruction preference
    geminiKey: process.env.API_KEY || '', // Automatically picks up from env if injected
    mistralKey: '',
  });

  const [activeTab, setActiveTab] = useState<'input' | 'preview'>('input');

  const handleGenerate = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    const key = state.provider === AIProvider.GEMINI ? state.geminiKey : state.mistralKey;
    
    try {
      if (!key) throw new Error(`Please enter an API Key for ${state.provider}`);
      const result = await generateMMSS(state.inputText, state.provider, key);
      setState(prev => ({ ...prev, jsonOutput: result, isLoading: false }));
    } catch (err: any) {
      setState(prev => ({ ...prev, error: err.message, isLoading: false }));
    }
  };

  const copyToClipboard = () => {
    if (state.jsonOutput) {
      navigator.clipboard.writeText(JSON.stringify(state.jsonOutput, null, 2));
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 lg:p-6 flex flex-col font-sans">
      
      {/* Header */}
      <header className="mb-6 flex justify-between items-end border-b border-slate-800 pb-4">
        <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            MMSS Forge
            </h1>
            <p className="text-slate-400 text-sm mt-1">Universal System Meta-Layer Converter</p>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-500">
            <span className={`px-2 py-1 rounded ${state.provider === AIProvider.GEMINI ? 'bg-blue-900/50 text-blue-200 border border-blue-700' : 'bg-slate-800'}`}>Gemini 2.5 Flash</span>
            <span className={`px-2 py-1 rounded ${state.provider === AIProvider.MISTRAL ? 'bg-indigo-900/50 text-indigo-200 border border-indigo-700' : 'bg-slate-800'}`}>Mistral</span>
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Configuration & Input */}
        <div className="lg:col-span-4 flex flex-col gap-4">
            
            {/* AI Config Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
                <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">Intelligence Engine</h2>
                
                <div className="flex gap-2 mb-4">
                    <button 
                        onClick={() => setState(s => ({...s, provider: AIProvider.GEMINI}))}
                        className={`flex-1 py-2 text-sm rounded-md transition-all font-medium ${state.provider === AIProvider.GEMINI ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                    >
                        Gemini
                    </button>
                    <button 
                         onClick={() => setState(s => ({...s, provider: AIProvider.MISTRAL}))}
                        className={`flex-1 py-2 text-sm rounded-md transition-all font-medium ${state.provider === AIProvider.MISTRAL ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/20' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                    >
                        Mistral
                    </button>
                </div>

                <div className="space-y-2">
                    <label className="text-xs text-slate-400">
                        {state.provider === AIProvider.GEMINI ? 'Gemini API Key' : 'Mistral API Key'}
                    </label>
                    <input 
                        type="password" 
                        className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                        placeholder="sk-..."
                        value={state.provider === AIProvider.GEMINI ? state.geminiKey : state.mistralKey}
                        onChange={(e) => {
                            const val = e.target.value;
                            setState(s => state.provider === AIProvider.GEMINI ? {...s, geminiKey: val} : {...s, mistralKey: val});
                        }}
                    />
                </div>
            </div>

            {/* Input Card */}
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col min-h-[300px]">
                <h2 className="text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wider">System Description</h2>
                <textarea 
                    className="flex-1 w-full bg-slate-950 border border-slate-700 rounded p-3 text-sm font-mono text-slate-300 leading-relaxed focus:outline-none focus:border-blue-500 resize-none"
                    value={state.inputText}
                    onChange={(e) => setState(s => ({...s, inputText: e.target.value}))}
                    placeholder="Describe your system (physics, sociology, software, etc.) here..."
                />
                <button 
                    disabled={state.isLoading}
                    onClick={handleGenerate}
                    className="mt-4 w-full bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-bold py-3 px-4 rounded-lg shadow-lg shadow-blue-900/20 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {state.isLoading ? (
                        <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Processing...
                        </span>
                    ) : (
                        "Convert to MMSS"
                    )}
                </button>
                {state.error && (
                    <div className="mt-3 p-3 bg-red-900/20 border border-red-800 rounded text-red-300 text-xs">
                        {state.error}
                    </div>
                )}
            </div>
        </div>

        {/* Center/Right Column: Output & Visuals */}
        <div className="lg:col-span-8 flex flex-col gap-6">
            
            {/* Visualizer (Top Half) */}
            <div className="h-[400px] bg-slate-900 border border-slate-800 rounded-xl p-1 shadow-lg flex flex-col">
                 <div className="px-4 py-2 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 rounded-t-xl">
                    <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Topology Visualizer</h2>
                    <span className="text-xs text-slate-500">Force-Directed Graph</span>
                </div>
                <div className="flex-1 p-2 bg-slate-950/50 rounded-b-xl overflow-hidden">
                    <NetworkVisualizer data={state.jsonOutput} />
                </div>
            </div>

            {/* JSON Output (Bottom Half) */}
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-1 shadow-lg flex flex-col min-h-[400px]">
                 <div className="px-4 py-2 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 rounded-t-xl">
                    <div className="flex gap-4">
                        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">JSON Output</h2>
                    </div>
                    <button 
                        onClick={copyToClipboard}
                        disabled={!state.jsonOutput}
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded transition-colors disabled:opacity-50"
                    >
                        Copy JSON
                    </button>
                </div>
                <div className="flex-1 relative bg-slate-950 overflow-hidden rounded-b-xl">
                    <div className="absolute inset-0 overflow-auto p-4">
                        {state.jsonOutput ? (
                             <RecursiveJsonViewer data={state.jsonOutput.MMSS_UNIVERSAL_TEMPLATE} level={0} />
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-slate-600">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                </svg>
                                <p className="font-mono text-sm">Awaiting MMSS Generation</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

// Simple recursive JSON viewer for better aesthetics than just <pre>
const RecursiveJsonViewer: React.FC<{data: any, level: number}> = ({data, level}) => {
    if (typeof data === 'object' && data !== null) {
        if (Array.isArray(data)) {
            if (data.length === 0) return <span className="text-slate-500">[]</span>;
            return (
                <div className="font-mono text-sm">
                    <span className="text-yellow-600">[</span>
                    <div className="pl-4 border-l border-slate-800 ml-1">
                        {data.map((item, idx) => (
                            <div key={idx} className="my-1">
                                <RecursiveJsonViewer data={item} level={level + 1} />
                                {idx < data.length - 1 && <span className="text-slate-600">,</span>}
                            </div>
                        ))}
                    </div>
                    <span className="text-yellow-600">]</span>
                </div>
            );
        } else {
             const keys = Object.keys(data);
             if (keys.length === 0) return <span className="text-slate-500">{"{}"}</span>;
             return (
                 <div className="font-mono text-sm">
                    <span className="text-purple-400">{"{"}</span>
                    <div className="pl-4 border-l border-slate-800 ml-1">
                        {keys.map((key, idx) => (
                            <div key={key} className="my-1">
                                <span className="text-blue-400">"{key}"</span>
                                <span className="text-slate-400 mr-2">:</span>
                                <RecursiveJsonViewer data={data[key]} level={level + 1} />
                                {idx < keys.length - 1 && <span className="text-slate-600">,</span>}
                            </div>
                        ))}
                    </div>
                    <span className="text-purple-400">{"}"}</span>
                 </div>
             )
        }
    }
    
    if (typeof data === 'string') return <span className="text-emerald-300">"{data}"</span>;
    if (typeof data === 'number') return <span className="text-orange-300">{data}</span>;
    if (typeof data === 'boolean') return <span className="text-pink-400">{data.toString()}</span>;
    return <span className="text-slate-500">null</span>;
}

export default App;
