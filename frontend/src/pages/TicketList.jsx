import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import {
    Plus, Filter, MessageSquare, AlertCircle, Search,
    ChevronRight, ArrowRight, User as UserIcon, Calendar, CheckCircle,
    Frown, Smile, Meh
} from 'lucide-react';
import CreateTicketModal from '../components/Tickets/CreateTicketModal';

export default function TicketList() {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('ALL'); // ALL, OPEN, PROGRESS, RESOLVED

    const fetchTickets = async () => {
        try {
            const res = await api.get('/tickets/');
            setTickets(res.data.results || res.data);
        } catch (err) {
            console.error('Erro ao buscar tickets', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTickets();
        const interval = setInterval(fetchTickets, 8000); // 8 sec auto refresh fila
        return () => clearInterval(interval);
    }, []);

    const filteredTickets = tickets.filter(t => {
        const matchesSearch = t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            String(t.id).toLowerCase().includes(searchTerm.toLowerCase());

        if (statusFilter === 'ALL') return matchesSearch;
        if (statusFilter === 'OPEN') return matchesSearch && (t.status === 'OPEN' || t.status === 'REOPENED');
        if (statusFilter === 'PROGRESS') return matchesSearch && (t.status === 'PROGRESS' || t.status === 'WAITING_USER' || t.status === 'PENDING_TECH');
        if (statusFilter === 'RESOLVED') return matchesSearch && t.status === 'RESOLVED';

        return matchesSearch;
    });

    const onTicketCreated = (newTicket) => {
        setTickets([newTicket, ...tickets]);
    };

    if (loading) return (
        <div className="flex items-center justify-center min-h-[60vh]">
            <div className="animate-pulse text-brand-500 font-medium">Carregando fila de atendimentos...</div>
        </div>
    );

    return (
        <div className="space-y-8 fade-in">
            <header className="flex flex-col lg:flex-row justify-between items-start lg:items-center bg-white dark:bg-surface-900 p-8 rounded-3xl border border-surface-200 dark:border-white/5 shadow-premium gap-6 relative overflow-hidden group transition-all duration-500">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-500/5 rounded-full blur-3xl group-hover:bg-brand-500/10 transition-all duration-700"></div>
                <div className="relative z-10">
                    <h1 className="text-3xl lg:text-4xl font-black text-surface-900 dark:text-white tracking-tight italic uppercase leading-none">Fila de Chamados</h1>
                    <p className="text-surface-500 dark:text-surface-400 text-sm lg:text-lg mt-2 font-medium italic">Gestão centralizada de ocorrências técnicas.</p>
                </div>
                <div className="flex flex-col sm:flex-row items-center w-full lg:w-auto gap-4">
                    <div className="relative w-full sm:w-auto flex-1">
                        <Search className="absolute left-4 top-4 text-surface-400 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Buscar ID ou assunto..."
                            className="w-full sm:w-80 pl-12 pr-6 py-4 bg-white dark:bg-surface-800 border border-surface-200 dark:border-white/10 rounded-2xl focus:ring-4 focus:ring-brand-500/10 outline-none transition-all font-medium text-surface-900 dark:text-white shadow-sm"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="w-full sm:w-auto btn-primary flex items-center justify-center space-x-3 bg-brand-600 hover:bg-brand-700 text-white shadow-xl shadow-brand-500/30 px-8 py-4 rounded-2xl font-black transition-all"
                    >
                        <Plus size={24} />
                        <span>Novo Chamado</span>
                    </button>
                </div>
            </header>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 px-2">
                <div className="flex items-center p-1 bg-white dark:bg-surface-900 rounded-2xl border border-surface-200 dark:border-white/5 overflow-x-auto w-full sm:w-auto whitespace-nowrap scrollbar-hide shadow-soft">
                    <FilterButton
                        label="Todos"
                        active={statusFilter === 'ALL'}
                        count={tickets.length}
                        onClick={() => setStatusFilter('ALL')}
                    />
                    <FilterButton
                        label="Pendentes"
                        active={statusFilter === 'OPEN'}
                        count={tickets.filter(t => t.status === 'OPEN' || t.status === 'REOPENED').length}
                        onClick={() => setStatusFilter('OPEN')}
                    />
                    <FilterButton
                        label="Em Atendimento"
                        active={statusFilter === 'PROGRESS'}
                        count={tickets.filter(t => ['PROGRESS', 'WAITING_USER', 'PENDING_TECH'].includes(t.status)).length}
                        onClick={() => setStatusFilter('PROGRESS')}
                    />
                    <FilterButton
                        label="Concluídos"
                        active={statusFilter === 'RESOLVED'}
                        count={tickets.filter(t => t.status === 'RESOLVED').length}
                        onClick={() => setStatusFilter('RESOLVED')}
                    />
                </div>
                <div className="text-[10px] font-black uppercase tracking-widest text-surface-400 italic">
                    Mostrando {filteredTickets.length} de {tickets.length} chamados
                </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
                {filteredTickets.length > 0 ? (
                    filteredTickets.map(ticket => (
                        <Link
                            key={ticket.id}
                            to={`/tickets/${ticket.id}`}
                            className="bg-white dark:bg-surface-900 p-6 rounded-3xl border border-surface-200 dark:border-white/5 flex items-center justify-between hover:translate-x-2 transition-all duration-500 group cursor-pointer relative overflow-hidden shadow-soft"
                        >
                            {/* Priority Indicator Stripe */}
                            <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${getPriorityBg(ticket.priority)}`}></div>

                            <div className="flex items-center space-x-6 flex-1 relative z-10">
                                <div className={`p-4 rounded-2xl bg-gradient-to-br ${getStatusBgGradient(ticket.status)} border ${getStatusBorder(ticket.status)} shadow-lg group-hover:scale-110 transition-transform duration-500`}>
                                    <AlertCircle className={getStatusText(ticket.status)} size={24} />
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="flex flex-wrap items-center gap-3 mb-2">
                                        <span className="text-[9px] bg-brand-50/50 dark:bg-surface-800 text-brand-500 dark:text-surface-500 font-black px-2 py-1 rounded-lg uppercase tracking-widest border border-brand-100 dark:border-white/5">#{ticket.id}</span>

                                        {/* Badge de Sentimento IA */}
                                        <div className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-[9px] font-black uppercase tracking-wider border shadow-sm ${getSentimentStyle(ticket.sentiment)}`}>
                                            {ticket.sentiment === 'ANGRY' && <Frown size={12} className="animate-pulse" />}
                                            {ticket.sentiment === 'POSITIVE' && <Smile size={12} />}
                                            {ticket.sentiment === 'NEUTRAL' && <Meh size={12} />}
                                            <span>{translateSentiment(ticket.sentiment)}</span>
                                        </div>
                                    </div>

                                    <h3 className="text-xl font-black text-surface-900 dark:text-white group-hover:text-brand-500 transition-colors uppercase italic truncate tracking-tighter leading-none">{ticket.title}</h3>

                                    <div className="flex flex-wrap items-center gap-6 mt-4">
                                        <div className="flex items-center text-[10px] text-surface-500 dark:text-surface-400 font-bold uppercase tracking-[0.2em]">
                                            <UserIcon size={14} className="mr-2 text-brand-500" />
                                            {ticket.created_by?.first_name || 'Usuário'}
                                        </div>
                                        <div className="flex items-center text-[10px] text-surface-500 dark:text-surface-400 font-bold uppercase tracking-[0.2em]">
                                            <Calendar size={14} className="mr-2 text-brand-500" />
                                            {new Date(ticket.created_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center space-x-6 relative z-10">
                                <div className="text-right hidden md:block border-r border-surface-100 dark:border-white/5 pr-6 mr-2">
                                    <p className="text-[10px] font-black text-surface-400 dark:text-surface-500 uppercase tracking-widest mb-1.5 leading-none">Prioridade</p>
                                    <span className={`text-xs font-black italic uppercase px-3 py-1 rounded-lg ${getPriorityBadgeColor(ticket.priority)}`}>
                                        {translatePriority(ticket.priority)}
                                    </span>
                                </div>
                                <div className="w-12 h-12 flex items-center justify-center bg-surface-50 dark:bg-surface-800/50 text-surface-400 dark:text-surface-500 rounded-2xl group-hover:bg-brand-600 group-hover:text-white group-hover:shadow-xl group-hover:shadow-brand-500/40 transition-all duration-500 border border-surface-100 dark:border-white/5">
                                    <ChevronRight size={24} className="group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        </Link>
                    ))
                ) : (
                    <div className="p-20 text-center glass-card border-dashed border-2 border-surface-200">
                        <p className="text-surface-400 font-black uppercase tracking-widest">Nenhum chamado encontrado na fila.</p>
                    </div>
                )}
            </div>

            <CreateTicketModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onTicketCreated={onTicketCreated}
            />
        </div>
    );
}

function getStatusBgGradient(status) {
    switch (status) {
        case 'OPEN': return 'from-blue-500/10 to-blue-600/5';
        case 'PENDING_TECH': return 'from-purple-500/10 to-purple-600/5';
        case 'WAITING_USER': return 'from-amber-500/10 to-amber-600/5';
        case 'PROGRESS': return 'from-cyan-500/10 to-cyan-600/5';
        case 'REOPENED': return 'from-red-500/20 to-red-600/20 animate-pulse';
        case 'RESOLVED': return 'from-emerald-500/10 to-emerald-600/5';
        default: return 'from-surface-100 to-surface-200';
    }
}

function getPriorityBadgeColor(priority) {
    switch (priority) {
        case 'CRITICAL': return 'bg-red-500 text-white shadow-lg shadow-red-500/40';
        case 'HIGH': return 'bg-amber-500 text-white shadow-lg shadow-amber-500/40';
        case 'MEDIUM': return 'bg-brand-500 text-white shadow-lg shadow-brand-500/40';
        case 'LOW': return 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/40';
        default: return 'bg-surface-400 text-white';
    }
}

function getStatusBorder(status) {
    switch (status) {
        case 'OPEN': return 'border-blue-100';
        case 'PENDING_TECH': return 'border-purple-200';
        case 'WAITING_USER': return 'border-amber-200';
        case 'PROGRESS': return 'border-cyan-100';
        case 'REOPENED': return 'border-red-600';
        case 'RESOLVED': return 'border-green-100';
        default: return 'border-surface-100';
    }
}

function getStatusText(status) {
    switch (status) {
        case 'OPEN': return 'text-blue-500';
        case 'PENDING_TECH': return 'text-purple-600';
        case 'WAITING_USER': return 'text-amber-600';
        case 'PROGRESS': return 'text-cyan-500';
        case 'REOPENED': return 'text-white font-black'; // Texto branco puro quando pulsa
        case 'RESOLVED': return 'text-green-500';
        default: return 'text-surface-400';
    }
}

function getPriorityColor(priority) {
    switch (priority) {
        case 'HIGH':
        case 'CRITICAL': return 'text-red-500';
        case 'MEDIUM': return 'text-amber-500';
        default: return 'text-brand-500';
    }
}

function getSentimentStyle(sentiment) {
    if (!sentiment) return 'bg-brand-50/50 text-brand-600 border-brand-100';
    switch (sentiment) {
        case 'ANGRY': return 'bg-red-50 text-red-600 border-red-100';
        case 'POSITIVE': return 'bg-emerald-50 text-emerald-600 border-emerald-100';
        default: return 'bg-brand-50/50 text-brand-600 border-brand-100';
    }
}
function translateSentiment(sentiment) {
    if (!sentiment) return 'NEUTRO';
    switch (sentiment) {
        case 'ANGRY': return 'NEGATIVO';
        case 'POSITIVE': return 'POSITIVO';
        default: return 'NEUTRO';
    }
}

function translatePriority(priority) {
    switch (priority) {
        case 'CRITICAL': return 'CRÍTICA';
        case 'HIGH': return 'ALTA';
        case 'MEDIUM': return 'MÉDIA';
        case 'LOW': return 'BAIXA';
        default: return priority;
    }
}

function getPriorityBg(priority) {
    switch (priority) {
        case 'CRITICAL': return 'bg-red-500';
        case 'HIGH': return 'bg-amber-500';
        case 'MEDIUM': return 'bg-brand-500';
        default: return 'bg-emerald-500';
    }
}
function FilterButton({ label, active, onClick, count }) {
    return (
        <button
            onClick={onClick}
            className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center space-x-2 ${active
                ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/20'
                : 'text-surface-400 hover:bg-brand-50/50 hover:text-surface-600 dark:hover:bg-surface-700/50'
                }`}
        >
            <span>{label}</span>
            <span className={`px-1.5 py-0.5 rounded-md text-[8px] ${active ? 'bg-white/20' : 'bg-surface-100 dark:bg-surface-900 border border-surface-200/50 dark:border-white/5'}`}>
                {count}
            </span>
        </button>
    );
}
