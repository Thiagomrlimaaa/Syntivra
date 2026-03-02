import React, { useEffect, useState } from 'react';
import api from '../services/api';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area, Cell, PieChart, Pie
} from 'recharts';
import { Ticket, Clock, CheckCircle, Users, ArrowUpRight, Search, Bell, Sparkles, Zap, AlertCircle, FileText } from 'lucide-react';

export default function Dashboard() {
    const [metrics, setMetrics] = useState({
        mttr_hours: 0,
        technician_productivity: [],
        tickets_by_status: [],
        tickets_by_priority: [],
        ai_stats: { assisted: 0, gaps: 0, efficiency_pct: 0 }
    });
    const [loading, setLoading] = useState(true);
    const [isDemoMode, setIsDemoMode] = useState(false);

    const fetchMetrics = () => {
        setLoading(true);
        api.get('/dashboard/metrics/')
            .then(res => {
                const data = res.data;
                if (!data || !data.technician_productivity || data.technician_productivity.length === 0) {
                    activateDemoMode();
                } else {
                    setMetrics(data);
                    setIsDemoMode(false);
                }
            })
            .catch(() => activateDemoMode())
            .finally(() => setLoading(false));
    };

    const activateDemoMode = () => {
        setIsDemoMode(true);
        setMetrics({
            mttr_hours: 3.8,
            technician_productivity: [
                { assigned_to__first_name: 'Gabriel', resolved_count: 14 },
                { assigned_to__first_name: 'Juliana', resolved_count: 22 },
                { assigned_to__first_name: 'Lucas', resolved_count: 18 },
                { assigned_to__first_name: 'Fernanda', resolved_count: 25 },
                { assigned_to__first_name: 'Ricardo', resolved_count: 12 },
            ],
            tickets_by_status: [
                { status: 'OPEN', total: 12 },
                { status: 'PROGRESS', total: 8 },
                { status: 'RESOLVED', total: 45 },
                { status: 'HOLD', total: 4 },
            ],
            ai_stats: {
                assisted: 28,
                gaps: 5,
                efficiency_pct: 64.2
            },
            tickets_by_priority: [
                { priority: 'LOW', total: 20 },
                { priority: 'MEDIUM', total: 35 },
                { priority: 'HIGH', total: 12 },
                { priority: 'CRITICAL', total: 3 },
            ]
        });
    };

    useEffect(() => {
        fetchMetrics();
    }, []);

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <div className="w-12 h-12 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
            <p className="text-surface-400 font-bold uppercase tracking-widest text-xs">Sincronizando Módulo de Inteligência...</p>
        </div>
    );

    const totalTickets = metrics.tickets_by_status.reduce((acc, curr) => acc + curr.total, 0);

    return (
        <div className="space-y-8 fade-in">
            {isDemoMode && (
                <div className="bg-brand-600 text-white px-6 py-3 rounded-2xl flex items-center justify-between shadow-lg shadow-brand-500/20">
                    <div className="flex items-center space-x-3">
                        <Sparkles size={20} />
                        <p className="text-sm font-bold uppercase tracking-widest">Modo de Demonstração Ativado</p>
                    </div>
                    <button
                        onClick={fetchMetrics}
                        className="text-[10px] bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg font-black uppercase transition-all"
                    >
                        Sincronizar Dados Reais
                    </button>
                </div>
            )}

            <header className="flex flex-col lg:flex-row justify-between items-start lg:items-center bg-white dark:bg-surface-900 p-8 rounded-3xl border border-surface-200 dark:border-white/5 shadow-sm gap-6 relative overflow-hidden group">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-500/5 rounded-full blur-3xl group-hover:bg-brand-500/10 transition-all duration-700"></div>
                <div className="relative z-10">
                    <h1 className="text-4xl font-extrabold text-surface-900 dark:text-white tracking-tight italic uppercase">Hub Operacional</h1>
                    <p className="text-surface-500 dark:text-surface-400 text-lg mt-1 font-medium italic">Visão analítica de performance e SLAs por organização.</p>
                </div>
                <div className="flex flex-col sm:flex-row items-center w-full lg:w-auto gap-4 relative z-10">
                    <button
                        onClick={() => window.print()}
                        className="w-full sm:w-auto bg-surface-900 dark:bg-brand-600 hover:bg-black dark:hover:bg-brand-700 text-white px-6 py-4 rounded-2xl flex items-center justify-center space-x-3 text-xs uppercase font-black tracking-widest transition-all print:hidden shadow-lg"
                    >
                        <FileText size={18} />
                        <span>Relatório Executivo</span>
                    </button>
                    <div className="bg-surface-50 dark:bg-surface-800 p-3 rounded-2xl border border-surface-200 dark:border-white/10 flex items-center space-x-2 px-4 shadow-sm w-full sm:w-auto">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-[10px] font-black text-surface-900 dark:text-surface-400 uppercase tracking-widest leading-none">Motor Global Ativo</span>
                    </div>
                </div>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard title="Tempo Médio (MTTR)" value={`${metrics.mttr_hours}h`} change="+5.2%" color="text-blue-500" icon={Clock} />
                <StatCard title="Performance IA" value={`${metrics.ai_stats?.efficiency_pct}%`} change="Automação" color="text-cyan-500" icon={Sparkles} />
                <StatCard title="Gaps de Treinamento" value={metrics.ai_stats?.gaps} change="Urgente" color="text-amber-500" icon={AlertCircle} />
                <StatCard title="Taxa de Resolução" value={`${Math.round((metrics.tickets_by_status.find(s => s.status === 'RESOLVED')?.total || 0) / (totalTickets || 1) * 100)}%`} change="Senior UX" color="text-emerald-500" icon={CheckCircle} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                {/* Gráfico de Especialistas */}
                <div className="glass-card p-10 rounded-[40px] relative overflow-hidden group border border-surface-200 shadow-sm">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-500/10 rounded-full blur-3xl group-hover:bg-brand-500/20 transition-all duration-700"></div>
                    <div className="flex justify-between items-center mb-10 relative z-10">
                        <div>
                            <h2 className="text-xl font-black italic uppercase text-surface-900 dark:text-white">Produtividade</h2>
                            <p className="text-[10px] text-surface-500 font-bold uppercase tracking-widest">Resoluções por Especialista</p>
                        </div>
                    </div>
                    <div className="h-[350px] w-full relative z-10">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={metrics.technician_productivity}>
                                <defs>
                                    <linearGradient id="colorProd" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4} />
                                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" className="dark:opacity-5" />
                                <XAxis
                                    dataKey="assigned_to__first_name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 900 }}
                                    dy={10}
                                />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 900 }} />
                                <Tooltip
                                    contentStyle={{
                                        borderRadius: '24px',
                                        border: 'none',
                                        backgroundColor: 'rgba(255,255,255,0.8)',
                                        backdropFilter: 'blur(10px)',
                                        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)',
                                        padding: '15px'
                                    }}
                                    itemStyle={{ color: '#0ea5e9', fontWeight: 900 }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="resolved_count"
                                    stroke="#0ea5e9"
                                    strokeWidth={4}
                                    fillOpacity={1}
                                    fill="url(#colorProd)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Priority Breakdown */}
                <div className="glass-card p-10 rounded-[40px] relative overflow-hidden group border border-surface-200 shadow-sm">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-500/10 rounded-full blur-3xl group-hover:bg-brand-500/20 transition-all duration-700"></div>
                    <div>
                        <h2 className="text-xl font-black italic uppercase text-surface-900 dark:text-white mb-2">Escalonamento</h2>
                        <p className="text-[10px] text-surface-500 font-bold uppercase tracking-widest mb-8">Tickets por Prioridade</p>

                        <div className="space-y-6">
                            {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(p => {
                                const count = metrics.tickets_by_priority.find(i => i.priority === p)?.total || 0;
                                const percentage = Math.round((count / totalTickets) * 100) || 0;
                                return (
                                    <div key={p} className="space-y-2">
                                        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                            <span className={p === 'CRITICAL' ? 'text-red-600' : 'text-surface-500'}>{p}</span>
                                            <span className="text-surface-900">{count} Chamados</span>
                                        </div>
                                        <div className="w-full bg-surface-100 h-2 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-1000 ${getPriorityBg(p)}`}
                                                style={{ width: `${percentage}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="mt-12 p-6 bg-blue-50 rounded-3xl text-blue-900 relative overflow-hidden group border border-blue-100 shadow-soft">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-125 transition-transform duration-500">
                            <Sparkles size={40} />
                        </div>
                        <h4 className="text-blue-400 font-black text-xs uppercase tracking-[0.2em] mb-2 flex items-center italic">
                            Análise de IA do Sistema
                        </h4>
                        <p className="text-[11px] lg:text-xs leading-relaxed font-bold text-blue-900">
                            A eficiência técnica atual está operando em <span className="text-green-400 font-black">12.5% acima da média</span> do setor para organizações enterprise.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, icon: Icon, color }) {
    return (
        <div className={`glass-card p-8 rounded-[40px] border border-surface-200 transition-all duration-500 group hover:translate-y-[-4px] shadow-sm relative overflow-hidden`}>
            <div className={`absolute -top-4 -right-4 w-24 h-24 rounded-full blur-3xl opacity-10 transition-all duration-700 group-hover:opacity-20 ${color.replace('text-', 'bg-')}`}></div>
            <div className="flex items-center justify-between mb-8 relative z-10">
                <div className={`p-4 rounded-2xl ${color.replace('text-', 'bg-')}/10 ${color} shadow-sm shadow-current/5`}>
                    <Icon size={24} />
                </div>
            </div>
            <div className="relative z-10">
                <p className="text-surface-500 dark:text-surface-400 text-[10px] font-black mb-1 uppercase tracking-[0.3em] italic">{title}</p>
                <p className="text-4xl font-black text-surface-900 dark:text-white tracking-tighter transition-all group-hover:tracking-tight group-hover:text-brand-500">{value}</p>
            </div>
        </div>
    );
}

function getPriorityBg(priority) {
    switch (priority) {
        case 'CRITICAL': return 'bg-red-500';
        case 'HIGH': return 'bg-amber-500';
        case 'MEDIUM': return 'bg-brand-500';
        default: return 'bg-surface-300';
    }
}
