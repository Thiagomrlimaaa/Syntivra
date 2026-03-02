import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Brain, Search, CheckCircle, ChevronRight, X, Zap, ArrowRight, Sparkles } from 'lucide-react';

export default function AITraining() {
    const [gaps, setGaps] = useState([]);
    const [selectedGap, setSelectedGap] = useState(null);
    const [solution, setSolution] = useState('');
    const [loading, setLoading] = useState(true);
    const [training, setTraining] = useState(false);

    useEffect(() => {
        fetchGaps();
    }, []);

    const fetchGaps = async () => {
        setLoading(true);
        try {
            const response = await api.get('/tickets/knowledge_gaps/');
            setGaps(response.data || []);
        } catch (err) {
            console.error('Erro ao buscar gaps reais:', err);
            // Em caso de erro, resetamos a lista
            setGaps([]);
        } finally {
            setLoading(false);
        }
    };

    const handleTrain = async () => {
        if (!solution.trim() || !selectedGap) return;
        setTraining(true);
        try {
            // Chamada Real para o Backend
            await api.post(`/tickets/${selectedGap.id}/train_ai/`, {
                solution: solution
            });

            setGaps(gaps.filter(g => g.id !== selectedGap.id));
            setSelectedGap(null);
            setSolution('');
            alert('Conhecimento injetado com sucesso no motor cognitivo!');
        } catch (err) {
            console.error('Erro no treinamento:', err);
            alert('Erro ao treinar IA. Verifique se o ticket ainda existe e tente novamente.');
        } finally {
            setTraining(false);
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <div className="w-12 h-12 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
            <p className="text-surface-400 font-bold uppercase tracking-widest text-[10px]">Sincronizando Banco de Dados Cognitivo...</p>
        </div>
    );

    return (
        <div className="space-y-8 fade-in h-full flex flex-col">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center glass-card p-8 rounded-3xl relative overflow-hidden group">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-500/10 rounded-full blur-3xl group-hover:bg-brand-500/20 transition-all duration-700"></div>
                <div className="relative z-10">
                    <h1 className="text-3xl font-black text-surface-900 dark:text-white tracking-tight italic uppercase flex items-center">
                        <Brain className="mr-3 text-brand-500 animate-pulse" size={32} />
                        Centro de Treinamento IA
                    </h1>
                    <p className="text-surface-500 dark:text-surface-400 text-sm mt-1 font-medium italic">Resolva os Gaps onde a IA falhou e ensine-a para o futuro.</p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 min-h-0">
                {/* Lista de Gaps */}
                <div className="lg:col-span-1 flex flex-col space-y-4 min-h-0">
                    <h3 className="text-[10px] font-black text-surface-400 dark:text-surface-500 uppercase tracking-[0.3em] ml-2 flex items-center">
                        Lacunas Pendentes ({gaps.length})
                    </h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-none">
                        {gaps.length === 0 ? (
                            <div className="p-12 text-center glass-card border-dashed border-2 border-brand-500/20 rounded-3xl">
                                <CheckCircle className="mx-auto mb-4 text-brand-500/30" size={48} />
                                <p className="text-surface-400 text-[10px] font-black uppercase tracking-widest">Todos os Gaps de Conhecimento foram resolvidos!</p>
                            </div>
                        ) : (
                            gaps.map(gap => (
                                <button
                                    key={gap.id}
                                    onClick={() => setSelectedGap(gap)}
                                    className={`w-full text-left p-5 rounded-2xl transition-all duration-300 border ${selectedGap?.id === gap.id
                                        ? 'bg-brand-600 text-white border-brand-400 shadow-xl shadow-brand-500/30 translate-x-1'
                                        : 'glass-card text-surface-900 dark:text-white border-surface-200 dark:border-white/5 hover:bg-surface-50 dark:hover:bg-surface-800'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <span className={`text-[8px] font-black px-1.5 py-0.5 rounded-md uppercase tracking-widest ${selectedGap?.id === gap.id ? 'bg-white/20' : 'bg-surface-100 dark:bg-surface-800'}`}>#{gap.id}</span>
                                        <span className={`text-[8px] font-black uppercase tracking-widest ${selectedGap?.id === gap.id ? 'text-white/70' : 'text-surface-400'}`}>
                                            {new Date(gap.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <h4 className="text-xs font-black uppercase italic truncate">{gap.title}</h4>
                                </button>
                            ))
                        )}
                    </div>
                </div>

                {/* Editor de Treinamento */}
                <div className="lg:col-span-2 min-h-0">
                    {selectedGap ? (
                        <div className="glass-card h-full flex flex-col rounded-3xl overflow-hidden relative group">
                            <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-brand-500/5 rounded-full blur-3xl group-hover:bg-brand-500/10 transition-all duration-700"></div>

                            <div className="p-8 border-b border-surface-50 dark:border-white/5 relative z-10">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="px-4 py-1.5 bg-brand-500 text-white rounded-full text-[9px] font-black uppercase tracking-widest flex items-center shadow-lg shadow-brand-500/20">
                                        <Zap size={12} className="mr-1.5" /> Gap Selecionado
                                    </div>
                                    <button onClick={() => setSelectedGap(null)} className="text-surface-400 hover:text-red-500 transition-colors">
                                        <X size={20} />
                                    </button>
                                </div>
                                <h2 className="text-2xl font-black text-brand-500 uppercase italic tracking-tight mb-2">{selectedGap.title}</h2>
                                <div className="bg-surface-50 dark:bg-surface-950 p-6 rounded-2xl border border-surface-200 dark:border-white/5 italic text-sm text-surface-600 dark:text-surface-400 leading-relaxed font-medium">
                                    <span className="text-[10px] font-black uppercase text-surface-400 block mb-2 not-italic tracking-widest">Dúvida do Cliente:</span>
                                    "{selectedGap.description}"
                                </div>
                            </div>

                            <div className="p-8 space-y-6 flex-1 flex flex-col relative z-10">
                                <div className="space-y-2 flex-1 flex flex-col">
                                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-surface-400 dark:text-surface-500 flex items-center ml-2">
                                        <ArrowRight size={12} className="mr-2 text-brand-500" /> Insira a Solução Mestra
                                    </label>
                                    <textarea
                                        value={solution}
                                        onChange={(e) => setSolution(e.target.value)}
                                        placeholder="Ex: Para configurar a assinatura digital, o usuário deve acessar o menu 'Minha Conta' e subir um arquivo .PNG..."
                                        className="w-full flex-1 p-6 bg-surface-50 dark:bg-surface-950 border-none rounded-3xl focus:ring-4 focus:ring-brand-500/10 transition-all outline-none font-medium text-sm text-surface-900 dark:text-white placeholder:italic resize-none ring-1 ring-surface-200 dark:ring-white/10"
                                    ></textarea>
                                </div>

                                <button
                                    onClick={handleTrain}
                                    disabled={training || !solution.trim()}
                                    className="w-full py-5 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white font-black rounded-3xl shadow-xl shadow-brand-500/30 transition-all active:scale-95 flex items-center justify-center space-x-3 text-sm uppercase tracking-widest disabled:grayscale disabled:opacity-50 group"
                                >
                                    {training ? (
                                        <div className="w-6 h-6 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
                                    ) : (
                                        <>
                                            <span>Injetar Conhecimento na IA</span>
                                            <Sparkles size={20} className="group-hover:rotate-12 transition-transform" />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center glass-card rounded-3xl border-dashed border-2 border-brand-500/10 p-20 text-center group">
                            <div className="w-24 h-24 bg-brand-500/10 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-700">
                                <Brain size={48} className="text-brand-500 opacity-40" />
                            </div>
                            <h3 className="text-xl font-black text-surface-900 dark:text-white uppercase tracking-tight italic mb-2">Selecione um Gap</h3>
                            <p className="max-w-xs text-xs text-surface-400 font-bold uppercase tracking-widest leading-loose">Clique em um chamado da lista ao lado para ensinar a IA como resolvê-lo.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
