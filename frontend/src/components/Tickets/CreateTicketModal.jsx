import React, { useState } from 'react';
import { X, AlertCircle, Send } from 'lucide-react';
import api from '../../services/api';

export default function CreateTicketModal({ isOpen, onClose, onTicketCreated }) {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [priority, setPriority] = useState('MEDIUM');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await api.post('/tickets/', {
                title,
                description,
                priority
            });
            onTicketCreated(response.data);
            onClose();
            // Reset form
            setTitle('');
            setDescription('');
            setPriority('MEDIUM');
        } catch (err) {
            setError('Erro ao criar chamado. Verifique os campos.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-surface-900/40 backdrop-blur-sm fade-in">
            <div className="bg-white w-full max-w-lg rounded-3xl shadow-2xl border border-surface-100 overflow-hidden">
                <header className="px-8 py-6 border-b border-surface-50 flex justify-between items-center bg-surface-50/30">
                    <div>
                        <h2 className="text-xl font-black text-surface-900">Novo Chamado</h2>
                        <p className="text-xs text-surface-500 font-bold uppercase tracking-wider mt-0.5">Abertura de Ticket Técnico</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-surface-100 rounded-xl transition-all">
                        <X size={20} className="text-surface-400" />
                    </button>
                </header>

                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    {error && (
                        <div className="p-4 bg-red-50 border border-red-100 text-red-700 text-xs font-bold rounded-2xl flex items-center">
                            <AlertCircle size={16} className="mr-2" />
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-surface-400 ml-1">Assunto do Ticket</label>
                        <input
                            type="text"
                            required
                            placeholder="Ex: Problema no acesso ao sistema"
                            className="w-full px-5 py-4 bg-surface-50 border-none rounded-2xl focus:ring-4 focus:ring-brand-500/10 outline-none transition-all font-medium"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-surface-400 ml-1">Nível de Prioridade</label>
                        <div className="grid grid-cols-3 gap-3">
                            {['LOW', 'MEDIUM', 'HIGH'].map(p => (
                                <button
                                    key={p}
                                    type="button"
                                    onClick={() => setPriority(p)}
                                    className={`py-3 rounded-2xl text-[10px] font-black transition-all border-2 ${priority === p
                                        ? 'bg-brand-50 border-brand-500 text-brand-700'
                                        : 'bg-white border-surface-100 text-surface-400 hover:border-surface-200'
                                        }`}
                                >
                                    {p === 'LOW' ? 'BAIXA' : p === 'MEDIUM' ? 'MÉDIA' : 'ALTA'}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-surface-400 ml-1">Descrição Detalhada</label>
                        <textarea
                            rows="4"
                            required
                            placeholder="Descreva o problema com o máximo de detalhes..."
                            className="w-full px-5 py-4 bg-surface-50 border-none rounded-2xl focus:ring-4 focus:ring-brand-500/10 outline-none transition-all font-medium resize-none"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                        ></textarea>
                    </div>

                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-black rounded-3xl shadow-xl shadow-brand-500/20 transition-all active:scale-95 flex items-center justify-center space-x-2"
                        >
                            {loading ? (
                                <div className="w-6 h-6 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    <span>Abrir Chamado</span>
                                    <Send size={18} />
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
