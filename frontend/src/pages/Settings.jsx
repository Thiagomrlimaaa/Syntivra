import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Shield, CreditCard, Bell, Save, Sparkles, CheckCircle2, Zap } from 'lucide-react';

export default function Settings() {
    const [modules, setModules] = useState({
        ai_suggestions: true,
        mfa_auth: false,
        audit_trail: true,
        auto_assign: true,
        sla_alerts: true
    });

    const [saving, setSaving] = useState(false);
    const [success, setSuccess] = useState(false);
    const [autoApproveIA, setAutoApproveIA] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem('@Syntivra:AutoAprovarIA') === 'true';
        setAutoApproveIA(saved);
    }, []);

    const toggleAutoApprove = () => {
        const newValue = !autoApproveIA;
        setAutoApproveIA(newValue);
        if (newValue) {
            localStorage.setItem('@Syntivra:AutoAprovarIA', 'true');
        } else {
            localStorage.removeItem('@Syntivra:AutoAprovarIA');
        }
    };

    const toggleModule = (key) => {
        setModules(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const handleSave = () => {
        setSaving(true);
        // Simula uma chamada de API Enterprise
        setTimeout(() => {
            setSaving(false);
            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        }, 1200);
    };

    return (
        <div className="space-y-8 fade-in">
            <header className="flex flex-col lg:flex-row justify-between items-start lg:items-center glass-card p-8 rounded-3xl border border-surface-200 dark:border-white/5 shadow-sm gap-6 relative overflow-hidden group">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-500/5 rounded-full blur-3xl group-hover:bg-brand-500/10 transition-all duration-700"></div>
                <div className="relative z-10">
                    <h1 className="text-4xl font-black text-surface-900 dark:text-white tracking-tight italic uppercase">Controle da Plataforma</h1>
                    <p className="text-surface-500 dark:text-surface-400 text-lg mt-1 font-medium italic">Gestão de segurança, inteligência e governança do seu painel.</p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="relative z-10 btn-primary flex items-center space-x-3 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-600 text-white shadow-lg shadow-brand-500/20 px-8 py-4 rounded-2xl font-black transition-all active:scale-95 disabled:opacity-70 whitespace-nowrap"
                >
                    {saving ? (
                        <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                    ) : success ? (
                        <CheckCircle2 size={24} />
                    ) : (
                        <Save size={24} />
                    )}
                    <span>{saving ? 'Sincronizando...' : success ? 'Configurações Salvas' : 'Salvar Alterações'}</span>
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {/* Core Modules */}
                <div className="lg:col-span-2 glass-card p-10 shadow-sm rounded-[40px]">
                    <div className="flex items-center space-x-4 mb-10 pb-6 border-b border-surface-200 dark:border-white/5">
                        <div className="p-4 bg-brand-500 text-white dark:bg-brand-500/10 dark:text-brand-500 rounded-3xl shadow-sm"><Shield size={28} /></div>
                        <div>
                            <h2 className="text-2xl font-black uppercase italic text-surface-900 dark:text-white leading-none">Central de Inteligência</h2>
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-surface-500 mt-2">Segurança & IA Ativa</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <ToggleItem
                            label="Auto-Aprovar Inteligência IA"
                            description="Todas as sugestões de alto nível da IA serão despachadas instantaneamente sem intervenção humana."
                            active={autoApproveIA}
                            onClick={toggleAutoApprove}
                            icon={<Zap size={18} className="text-brand-600" />}
                        />
                        <ToggleItem
                            label="Sugestões Cognitivas"
                            description="Utiliza IA treinada para sugerir respostas em tempo real baseada no histórico de tickets."
                            active={modules.ai_suggestions}
                            onClick={() => toggleModule('ai_suggestions')}
                        />
                        <ToggleItem
                            label="Atribuição Automática Round-Robin"
                            description="Distribuição inteligente de carga entre técnicos disponíveis da equipe."
                            active={modules.auto_assign}
                            onClick={() => toggleModule('auto_assign')}
                        />
                        <ToggleItem
                            label="Trilha de Auditoria Avançada"
                            description="Rastreabilidade imutável de todas as ações executadas no sistema por segurança e conformidade."
                            active={modules.audit_trail}
                            onClick={() => toggleModule('audit_trail')}
                        />
                        <ToggleItem
                            label="Alertas de SLA Preditivos"
                            description="Alertas de risco de quebra de SLA baseados no volume atual de atendimentos."
                            active={modules.sla_alerts}
                            onClick={() => toggleModule('sla_alerts')}
                        />
                        <ToggleItem
                            label="SAML / SSO Enforcement"
                            description="Obrigar login através do provedor de identidade corporativo da organização."
                            active={modules.mfa_auth}
                            onClick={() => toggleModule('mfa_auth')}
                        />
                    </div>
                </div>

                <div className="space-y-8">
                    <div className="glass-card p-8 shadow-sm rounded-[40px]">
                        <div className="flex items-center space-x-3 mb-6">
                            <Bell size={20} className="text-brand-500" />
                            <h3 className="text-xs font-black uppercase tracking-widest text-surface-900 dark:text-white">Notificações Críticas</h3>
                        </div>
                        <p className="text-xs text-surface-500 dark:text-surface-400 font-medium leading-relaxed">
                            As configurações de e-mail e webhooks (Discord/Slack) estão centralizadas em nível de organização e seguem as regras de conformidade LGPD.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ToggleItem({ label, description, active, onClick, icon }) {
    return (
        <div className="flex justify-between items-center py-6 border-b border-surface-200 dark:border-white/5 last:border-none group">
            <div className="flex-1 pr-8">
                <div className="flex items-center space-x-2 mb-1">
                    {icon}
                    <span className="text-lg font-black text-surface-900 dark:text-white uppercase italic tracking-tighter group-hover:text-brand-500 transition-colors leading-none">{label}</span>
                </div>
                <p className="text-[11px] lg:text-xs text-surface-500 dark:text-surface-400 font-semibold leading-relaxed max-w-sm">{description}</p>
            </div>
            <div
                onClick={onClick}
                className={`w-14 h-7 rounded-full relative cursor-pointer transition-all duration-300 ring-4 ring-offset-2 ring-transparent ${active ? 'bg-brand-500 ring-brand-500/20' : 'bg-surface-200 dark:bg-surface-800 hover:bg-surface-300 dark:hover:bg-surface-700'}`}
            >
                <div className={`w-5 h-5 bg-white rounded-full absolute top-1 shadow-md transition-all duration-300 ${active ? 'right-1' : 'left-1'}`}></div>
            </div>
        </div>
    );
}
