import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/useAuth';
import {
    Send, Bot, User as UserIcon, AlertTriangle,
    ArrowLeft, CheckCircle, Info, Sparkles, XCircle,
    Frown, Meh, Clock as ClockIcon, ThumbsUp, ThumbsDown,
    FileText, File, MessageSquare, Paperclip, ChevronRight, X, Calendar, Zap
} from 'lucide-react';

export default function TicketDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [ticket, setTicket] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const scrollRef = useRef(null);
    const fileInputRef = useRef(null);

    const fetchData = async () => {
        if (!id) return;
        try {
            const [ticketRes, messagesRes] = await Promise.all([
                api.get(`/tickets/${id}/`),
                api.get(`/tickets/${id}/messages/`)
            ]);
            setTicket(ticketRes.data);
            setMessages(Array.isArray(messagesRes.data) ? messagesRes.data : []);
        } catch (err) {
            console.error('Erro ao buscar dados do ticket:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, [id]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages.length]);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file || sending) return;

        setSending(true);
        const formData = new FormData();
        formData.append('file_attachment', file);
        formData.append('content', `Arquivo anexo: ${file.name}`);

        try {
            const res = await api.post(`/tickets/${id}/messages/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setMessages(prev => [...prev, res.data]);
        } catch (err) {
            console.error('Erro no upload', err);
        } finally {
            setSending(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleSendMessage = async (e) => {
        if (e) e.preventDefault();
        if (!newMessage.trim() || sending) return;

        setSending(true);
        try {
            const res = await api.post(`/tickets/${id}/messages/`, { content: newMessage });
            setMessages(prev => [...prev, res.data]);
            setNewMessage('');

            if (user?.role !== 'CUSTOMER') {
                const tr = await api.patch(`/tickets/${id}/`, { status: 'WAITING_USER' });
                setTicket(tr.data);
            }
        } catch (err) {
            console.error('Erro ao enviar mensagem', err);
        } finally {
            setSending(false);
        }
    };

    const handleApproveSuggestion = async (msg) => {
        try {
            // Envia como mensagem real do técnico
            const res = await api.post(`/tickets/${id}/messages/`, { content: msg.content });
            // Remove a sugestão original
            await api.delete(`/tickets/${id}/messages/${msg.id}/`);
            // Atualiza o ticket: Status + Track de performance IA positiva
            const tr = await api.patch(`/tickets/${id}/`, {
                status: 'WAITING_USER',
                ai_performance_score: 1,
                ai_assisted: true
            });
            setTicket(tr.data);
            setMessages(prev => [...prev.filter(m => m.id !== msg.id), res.data]);
        } catch (err) {
            console.error('Erro ao aprovar sugestão', err);
        }
    };

    const handleDiscardSuggestion = async (msgId) => {
        try {
            // Chamada para o endpoint que penaliza a IA e cria um GAP (Centro de Treinamento)
            const res = await api.post(`/tickets/${id}/messages/${msgId}/reject/`);
            setMessages(prev => prev.filter(m => m.id !== msgId));

            // Recarrega os dados do ticket para refletir o novo score de performance se necessário
            const ticketRes = await api.get(`/tickets/${id}/`);
            setTicket(ticketRes.data);

            alert(res.data.status || 'Sugestão descartada e enviada para treinamento.');
        } catch (err) {
            console.error('Erro ao descartar', err);
        }
    };

    const handleCustomerResolveAction = async (isSuccess) => {
        const newStatus = isSuccess ? 'RESOLVED' : 'REOPENED';
        try {
            const res = await api.patch(`/tickets/${id}/`, {
                status: newStatus,
                ai_performance_score: isSuccess ? 1 : -1
            });
            setTicket(res.data);
        } catch (err) {
            console.error('Erro ao confirmar resolução', err);
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <div className="w-12 h-12 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
            <p className="text-surface-400 font-bold uppercase tracking-widest text-[10px]">Auditando Histórico...</p>
        </div>
    );

    if (!ticket) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <XCircle className="text-red-500" size={48} />
            <p className="text-surface-900 dark:text-white font-black uppercase tracking-widest text-xs">Chamado não encontrado ou erro de conexão.</p>
            <button onClick={() => navigate('/tickets')} className="btn-primary mt-4 px-6 py-2 bg-brand-600 text-white rounded-xl">Voltar para a Lista</button>
        </div>
    );

    return (
        <div className="flex flex-col space-y-6 fade-in pb-12">
            {/* Header Responsivo Premium */}
            <header className="flex flex-col lg:flex-row justify-between items-start lg:items-center bg-white dark:bg-surface-900 p-6 lg:px-8 lg:py-4 rounded-3xl border border-surface-200 dark:border-white/5 relative overflow-hidden group shadow-premium transition-all duration-500">
                <div className="absolute -top-10 -right-10 w-32 h-32 bg-brand-500/10 rounded-full blur-3xl transition-all duration-700"></div>

                <div className="flex items-center space-x-6 w-full lg:w-auto relative z-10">
                    <button onClick={() => navigate('/tickets')} className="p-3 bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 text-surface-600 dark:text-surface-400 rounded-2xl transition-all border border-surface-200 dark:border-white/5 active:scale-90 shadow-sm">
                        <ArrowLeft size={18} />
                    </button>
                    <div>
                        <div className="flex items-center space-x-3">
                            <span className="text-[10px] font-black uppercase text-brand-600 dark:text-brand-400 tracking-widest bg-brand-50 dark:bg-brand-500/10 px-2 py-0.5 rounded-lg border border-brand-100 dark:border-brand-500/20 shadow-sm">#{String(ticket?.id || '').slice(0, 8)}</span>
                            <h1 className="text-xl font-black text-surface-900 dark:text-white uppercase italic truncate tracking-tight">{ticket?.title}</h1>
                        </div>
                        <p className="text-[10px] text-surface-500 dark:text-surface-400 font-bold uppercase tracking-widest mt-1">Status: <span className={getStatusText(ticket?.status)}>{translateStatus(ticket?.status)}</span></p>
                    </div>
                </div>

                <div className="flex items-center space-x-4 mt-4 lg:mt-0 w-full lg:w-auto relative z-10">
                    {ticket?.status !== 'RESOLVED' && (
                        <button
                            onClick={() => handleCustomerResolveAction(true)}
                            className="flex-1 lg:flex-none flex items-center justify-center space-x-2 px-6 py-3 bg-green-500 hover:bg-green-600 text-white font-black text-xs rounded-2xl shadow-lg shadow-green-500/20 transition-all uppercase tracking-widest active:scale-95"
                        >
                            <CheckCircle size={16} />
                            <span>Encerrar Ticket</span>
                        </button>
                    )}
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
                <div className="lg:col-span-3 flex flex-col space-y-6">
                    {/* Chat Box Premium */}
                    <div className="flex flex-col bg-white dark:bg-surface-900/60 backdrop-blur-md rounded-3xl shadow-premium min-h-[60vh] max-h-[75vh] relative overflow-hidden border border-surface-200 dark:border-white/5 transition-all duration-500">
                        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 lg:p-10 space-y-8 scrollbar-hide">
                            {/* Primeira Mensagem */}
                            <div className="flex justify-start">
                                <div className="max-w-[85%] bg-white dark:bg-surface-800 p-6 rounded-3xl border border-surface-200 dark:border-white/5 shadow-sm">
                                    <div className="flex items-center space-x-2 mb-4 opacity-70">
                                        <Info size={14} className="text-brand-500" />
                                        <span className="text-[10px] font-black uppercase tracking-widest text-surface-500 dark:text-surface-400">Descrição Inicial</span>
                                    </div>
                                    <p className="text-sm text-surface-900 dark:text-white leading-relaxed font-medium whitespace-pre-wrap">{ticket?.description}</p>
                                    <p className="text-[9px] mt-4 opacity-60 font-bold text-right italic text-surface-500 dark:text-surface-400">{ticket?.created_at ? new Date(ticket.created_at).toLocaleString() : ''}</p>
                                </div>
                            </div>

                            {messages.map((msg, idx) => {
                                const isAuth = msg.author?.id === user?.id;
                                const isAI = msg.is_ai_suggestion;

                                return (
                                    <div key={msg.id || idx} className={`flex ${isAI ? 'justify-start' : (isAuth ? 'justify-end' : 'justify-start')} group animate-slide-in`}>
                                        <div className={`max-w-[85%] relative ${isAI ? 'animate-float' : ''}`}>
                                            <div className={`flex items-center space-x-2 mb-1.5 px-2 ${isAI || !isAuth ? 'flex-row' : 'flex-row-reverse space-x-reverse'}`}>
                                                <span className="text-[9px] font-black uppercase tracking-widest text-brand-600 dark:text-surface-600 italic">
                                                    {isAI ? 'Syntivra Engine' : msg.author?.first_name || 'Agente'}
                                                </span>
                                                {isAI && <Sparkles size={10} className="text-brand-500 animate-pulse" />}
                                                <span className="text-[8px] text-surface-300 dark:text-surface-700 font-bold">{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                            </div>

                                            <div className={`p-5 rounded-3xl border transition-all duration-300 shadow-sm ${isAI
                                                ? 'bg-brand-500 text-white border-brand-400 rounded-tl-none ring-4 ring-brand-500/10'
                                                : !isAuth
                                                    ? 'bg-white dark:bg-surface-800 text-surface-900 dark:text-white border-surface-200 dark:border-white/5 rounded-tl-none'
                                                    : 'bg-surface-900 dark:bg-brand-600 text-white border-surface-800 dark:border-white/5 rounded-tr-none'
                                                }`}>

                                                <p className="text-sm leading-relaxed font-medium whitespace-pre-wrap">{msg.content}</p>

                                                {msg.file_attachment && (
                                                    <div className="mt-4">
                                                        <AttachmentPreview url={msg.file_attachment} />
                                                    </div>
                                                )}

                                                {isAI && user?.role !== 'CUSTOMER' && (
                                                    <div className="mt-6 flex flex-col space-y-2 pt-4 border-t border-white/20">
                                                        <button onClick={() => handleApproveSuggestion(msg)} className="w-full py-2 bg-white/20 hover:bg-white/30 text-white font-black text-[10px] uppercase rounded-xl transition-all">Aprovar e Enviar</button>
                                                        <div className="flex space-x-2">
                                                            <button onClick={() => setNewMessage(msg.content)} className="flex-1 py-2 bg-black/20 hover:bg-black/30 text-white font-black text-[9px] uppercase rounded-xl transition-all">Editar</button>
                                                            <button onClick={() => handleDiscardSuggestion(msg.id)} className="flex-1 py-2 bg-red-500/30 hover:bg-red-500/50 text-white font-black text-[9px] uppercase rounded-xl transition-all">Descartar</button>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}

                            {user?.role === 'CUSTOMER' && ticket?.status === 'WAITING_USER' && (
                                <div className="flex justify-center my-10 animate-bounce">
                                    <div className="glass-card p-8 rounded-[40px] border-brand-500/30 text-center max-w-sm">
                                        <CheckCircle className="mx-auto mb-4 text-brand-500" size={40} />
                                        <h3 className="text-sm font-black text-surface-900 dark:text-white uppercase tracking-tighter mb-6 underline decoration-brand-500 decoration-4 underline-offset-4">Resolvido?</h3>
                                        <div className="flex space-x-3">
                                            <button onClick={() => handleCustomerResolveAction(true)} className="flex-1 py-3 bg-green-500 text-white font-black text-xs uppercase rounded-2xl shadow-lg shadow-green-500/20 active:scale-90 transition-all">Sim</button>
                                            <button onClick={() => handleCustomerResolveAction(false)} className="flex-1 py-3 bg-red-500 text-white font-black text-xs uppercase rounded-2xl shadow-lg shadow-red-500/20 active:scale-90 transition-all">Não</button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <form onSubmit={handleSendMessage} className="p-6 bg-white dark:bg-surface-900 border-t border-surface-100 dark:border-white/5 relative z-10 transition-colors">
                            <div className="flex items-center space-x-4">
                                <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileUpload} />
                                <button type="button" onClick={() => fileInputRef.current?.click()} className="p-4 bg-surface-50 dark:bg-surface-800 text-surface-400 dark:text-surface-600 hover:text-brand-500 rounded-2xl border border-surface-100 dark:border-white/5 transition-all outline-none active:scale-90">
                                    <Paperclip size={20} />
                                </button>
                                <div className="relative flex-1">
                                    <input
                                        type="text"
                                        placeholder="Digite sua resposta mestre..."
                                        className="w-full px-6 py-4 bg-white dark:bg-surface-800 border border-surface-200 dark:border-white/10 rounded-3xl outline-none focus:ring-4 focus:ring-brand-500/10 transition-all font-bold italic text-sm text-surface-900 dark:text-white"
                                        value={newMessage}
                                        onChange={(e) => setNewMessage(e.target.value)}
                                        disabled={ticket?.status === 'RESOLVED'}
                                    />
                                    <button type="submit" disabled={!newMessage.trim() || sending} className="absolute right-2 top-2 p-2.5 bg-brand-600 text-white rounded-2xl hover:bg-brand-700 transition-all shadow-xl shadow-brand-500/20 disabled:grayscale">
                                        {sending ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> : <Send size={18} />}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <div className="lg:col-span-1 space-y-6">
                    {/* SLA Sidebar Premium */}
                    <div className="bg-white dark:bg-surface-900 p-8 rounded-3xl border border-surface-200 dark:border-white/5 group relative overflow-hidden shadow-soft transition-all duration-500">
                        <div className="absolute -top-10 -right-10 w-24 h-24 bg-brand-500/5 rounded-full blur-2xl group-hover:bg-brand-500/10 transition-all"></div>
                        <h3 className="text-[10px] font-black text-surface-400 dark:text-surface-500 uppercase tracking-[0.3em] mb-8 flex items-center italic">
                            <ClockIcon size={14} className="mr-3 text-brand-500 animate-pulse-slow" /> Tempo de Resolução
                        </h3>

                        <SLAProgress deadline={ticket?.sla_deadline} createdAt={ticket?.created_at} isResolved={ticket?.status === 'RESOLVED'} />

                        <div className="mt-10 space-y-4 pt-4 border-t border-surface-100 dark:border-white/5">
                            <InfoRow label="Prioridade" value={translatePriority(ticket?.priority)} />
                            <InfoRow label="Atribuído" value={ticket?.assigned_to?.first_name || 'Agente IA'} highlight="text-brand-500" />
                            <InfoRow label="Abertura" value={ticket?.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'N/A'} />
                        </div>
                    </div>

                    {/* Cognitive Insight Box */}
                    <div className="p-8 rounded-[40px] bg-surface-950 dark:bg-black text-white relative overflow-hidden shadow-2xl group border-t border-white/10">
                        <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:scale-125 transition-all duration-700">
                            <Zap size={60} />
                        </div>
                        <h4 className="text-brand-400 font-black text-[9px] uppercase tracking-[0.4em] mb-4 flex items-center italic">
                            <div className="w-1.5 h-1.5 bg-brand-500 rounded-full mr-2 animate-ping"></div>
                            Syntivra Cognitive
                        </h4>
                        <p className="text-xs font-bold leading-loose opacity-60">
                            A IA detectou sentimentos de <span className="text-brand-400 uppercase italic">urgência média</span>.
                            O motor de resposta está otimizado para resoluções técnicas de nível 2.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function InfoRow({ label, value, highlight }) {
    return (
        <div className="flex justify-between items-center text-[9px] font-black uppercase tracking-widest leading-none">
            <span className="text-surface-400 dark:text-surface-600">{label}</span>
            <span className={highlight || 'text-surface-900 dark:text-white italic'}>{value}</span>
        </div>
    );
}

function AttachmentPreview({ url }) {
    if (!url) return null;
    const isImage = /\.(jpeg|jpg|gif|png|webp)$/i.test(url);
    const isPDF = /\.pdf$/i.test(url);
    const fileName = url.split('/').pop().split('?')[0];

    return (
        <a href={url} target="_blank" rel="noreferrer" className="flex items-center space-x-3 p-3 bg-surface-50 dark:bg-surface-950/50 hover:bg-white dark:hover:bg-surface-800 rounded-2xl border border-surface-100 dark:border-white/5 transition-all group">
            <div className={`p-2 rounded-xl ${isPDF ? 'bg-red-500/10 text-red-500' : 'bg-brand-500/10 text-brand-500'}`}>
                {isPDF ? <FileText size={20} /> : <File size={20} />}
            </div>
            <div className="min-w-0">
                <p className="text-[10px] font-black text-surface-900 dark:text-white truncate">{fileName}</p>
                <p className="text-[8px] font-bold text-surface-400 uppercase tracking-widest">{isPDF ? 'DOC PDF' : 'Anexo Digital'}</p>
            </div>
        </a>
    );
}

function SLAProgress({ deadline, createdAt, isResolved }) {
    if (!deadline || isResolved) return (
        <div className="flex flex-col items-center">
            <div className="w-32 h-32 rounded-full border-4 border-green-500/20 flex items-center justify-center bg-green-500/5">
                <CheckCircle className="text-green-500 animate-pulse" size={32} />
            </div>
            <p className="mt-4 text-[10px] font-black uppercase text-green-500 tracking-[0.2em] italic">Meta Batida</p>
        </div>
    );

    const targetDate = new Date(deadline);
    const startDate = new Date(createdAt);
    const now = new Date();

    if (isNaN(targetDate.getTime()) || isNaN(startDate.getTime())) return null;

    const total = targetDate - startDate;
    const elapsed = now - startDate;
    const progress = Math.min(Math.max((elapsed / total) * 100, 0), 100);

    const radius = 55;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (progress / 100) * circumference;
    const color = progress > 80 ? '#ef4444' : progress > 50 ? '#f59e0b' : '#0ea5e9';

    return (
        <div className="relative flex flex-col items-center">
            <svg className="w-36 h-36 -rotate-90">
                <circle cx="72" cy="72" r={radius} fill="transparent" stroke="currentColor" strokeWidth="8" className="text-surface-100 dark:text-surface-800" />
                <circle cx="72" cy="72" r={radius} fill="transparent" stroke={color} strokeWidth="8" strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" className="transition-all duration-1000" />
            </svg>
            <div className="absolute top-[45px] flex flex-col items-center">
                <span className="text-2xl font-black text-surface-900 dark:text-white tracking-tighter">{Math.round(progress)}%</span>
                <span className="text-[8px] font-black text-surface-400 dark:text-surface-600 uppercase tracking-widest leading-none">SLA Consumed</span>
            </div>
        </div>
    );
}

function translateStatus(status) {
    if (!status) return '...';
    const map = { 'OPEN': 'ABERTO', 'PENDING_TECH': 'PENDENTE', 'WAITING_USER': 'AGUARDANDO', 'PROGRESS': 'EM CURSO', 'REOPENED': 'REABERTO', 'RESOLVED': 'RESOLVIDO' };
    return map[status] || status;
}

function translatePriority(p) {
    if (!p) return '...';
    const map = { 'CRITICAL': 'CRÍTICA', 'HIGH': 'ALTA', 'MEDIUM': 'MÉDIA', 'LOW': 'BAIXA' };
    return map[p] || p;
}

function getStatusText(s) {
    if (!s) return 'text-surface-400';
    const map = { 'OPEN': 'text-blue-500', 'PENDING_TECH': 'text-purple-500', 'WAITING_USER': 'text-amber-500', 'PROGRESS': 'text-cyan-500', 'REOPENED': 'text-red-500', 'RESOLVED': 'text-green-500' };
    return map[s] || 'text-surface-400';
}
