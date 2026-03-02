import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/useAuth';
import { Lock, Mail, Loader, ArrowRight, ShieldCheck, Zap } from 'lucide-react';

export default function Login() {
    const [cpf, setCpf] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const navigate = useNavigate();
    const setToken = useAuth(state => state.setToken);

    const formatCPF = (value) => {
        return value
            .replace(/\D/g, '') // Remove tudo que não é dígito
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d{1,2})/, '$1-$2')
            .replace(/(-\d{2})\d+?$/, '$1'); // Limita o tamanho
    };

    const handleCpfChange = (e) => {
        const maskedValue = formatCPF(e.target.value);
        setCpf(maskedValue);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const plainCpf = cpf.replace(/\D/g, ''); // Envia apenas números para o backend

        try {
            const response = await api.post('/users/login/', { cpf: plainCpf, password });
            setToken(response.data.access);
            navigate('/', { replace: true });
        } catch (err) {
            setError(err.response?.data?.detail || 'CPF ou Senha inválidos. Verifique os dados técnicos e tente novamente.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2 bg-surface-50 dark:bg-surface-950 font-sans transition-colors duration-500">
            {/* Coluna Visual - Lateral Esquerda */}
            <div className="hidden lg:flex relative bg-brand-950 items-center justify-center p-20 overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-full opacity-20 bg-[radial-gradient(circle_at_50%_50%,#38a9f8,transparent)] animate-pulse"></div>
                <div className="relative z-10 text-center max-w-lg">
                    <div className="inline-flex p-4 rounded-3xl bg-brand-500/10 border border-brand-500/20 mb-8 backdrop-blur-xl scale-110">
                        <ShieldCheck className="text-brand-400 w-12 h-12" />
                    </div>
                    <h2 className="text-5xl font-black text-white mb-6 leading-tight tracking-tight italic uppercase">Syntivra <span className="text-brand-400">OS</span></h2>
                    <p className="text-brand-200 text-xl leading-relaxed font-medium italic opacity-80">Architecture beyond convention. SaaS Multi-tenant with Active Intelligence.</p>

                    <div className="mt-16 grid grid-cols-3 gap-8">
                        <FeatureMini brand="99.9%" label="Segurança" />
                        <FeatureMini brand="0ms" label="Latência" />
                        <FeatureMini brand="v2.1" label="Versão" />
                    </div>
                </div>
            </div>

            {/* Coluna do Formulário */}
            <div className="flex items-center justify-center p-8 lg:p-24 fade-in bg-white dark:bg-surface-900 shadow-2xl z-10 transition-colors duration-500">
                <div className="max-w-md w-full">
                    <div className="mb-12 text-center lg:text-left">
                        <div className="inline-block px-3 py-1 bg-brand-600 text-white text-[10px] font-black uppercase tracking-[0.2em] rounded-lg mb-6 shadow-md border hover:scale-105 transition-all">Acesso Principal</div>
                        <h1 className="text-4xl lg:text-5xl font-black text-surface-900 dark:text-white mb-3 tracking-tighter italic uppercase drop-shadow-sm transition-colors">Autenticação</h1>
                        <p className="text-surface-600 dark:text-surface-400 font-bold uppercase text-xs tracking-widest mt-2 hover:text-surface-900 dark:hover:text-white transition-all cursor-default opacity-80">Informe suas credenciais para entrar no sistema.</p>
                    </div>

                    {error && (
                        <div className="mb-8 p-5 bg-red-100/50 dark:bg-red-500/10 text-red-900 dark:text-red-400 text-xs font-black uppercase tracking-widest rounded-2xl flex items-center shadow-xl shadow-red-500/10 border-l-8 border-red-500 animate-shake">
                            <span className="w-2 h-2 bg-red-500 rounded-full mr-4 animate-pulse"></span>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-3">
                            <label className="text-[10px] font-black text-surface-600 dark:text-surface-400 ml-1 uppercase tracking-[0.3em] italic leading-none">Acesso via CPF / ID</label>
                            <div className="relative group">
                                <ShieldCheck className="absolute left-5 top-5 text-surface-400 w-5 h-5 group-focus-within:text-brand-600 transition-all duration-300" />
                                <input
                                    type="text"
                                    required
                                    className="w-full pl-14 pr-6 py-5 bg-surface-50 dark:bg-surface-800 border-2 border-surface-200 dark:border-white/5 rounded-2xl focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 focus:bg-white dark:focus:bg-surface-900 outline-none transition-all font-black text-surface-900 dark:text-white shadow-inner text-lg tracking-wider"
                                    placeholder="000.000.000-00"
                                    value={cpf}
                                    onChange={handleCpfChange}
                                />
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div className="flex justify-between items-center px-1">
                                <label className="text-[10px] font-black text-surface-600 dark:text-surface-400 uppercase tracking-[0.3em] italic leading-none">Sua Senha</label>
                            </div>
                            <div className="relative group">
                                <Lock className="absolute left-5 top-5 text-surface-400 w-5 h-5 group-focus-within:text-brand-600 transition-all duration-300" />
                                <input
                                    type="password"
                                    required
                                    className="w-full pl-14 pr-6 py-5 bg-surface-50 dark:bg-surface-800 border-2 border-surface-200 dark:border-white/5 rounded-2xl focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 focus:bg-white dark:focus:bg-surface-900 outline-none transition-all font-black text-surface-900 dark:text-white shadow-inner text-lg tracking-widest"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-5 bg-brand-600 hover:bg-brand-700 text-white font-black text-sm uppercase tracking-[0.3em] rounded-2xl shadow-xl shadow-brand-500/30 transition-all active:scale-[0.96] flex items-center justify-center space-x-4 group mt-8 border-b-4 border-brand-800"
                        >
                            {loading ? (
                                <Loader className="animate-spin w-5 h-5" />
                            ) : (
                                <>
                                    <span>Acessar Painel</span>
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-2 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-12 text-center text-sm text-surface-400 font-medium">
                        Domínio protegido por criptografia de ponta-a-ponta e monitoramento em tempo real.
                    </div>
                </div>
            </div>
        </div>
    );
}

function FeatureMini({ brand, label }) {
    return (
        <div className="text-center">
            <p className="text-white font-black text-2xl">{brand}</p>
            <p className="text-brand-400 text-xs font-bold uppercase tracking-widest mt-1">{label}</p>
        </div>
    );
}
