import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/useAuth';
import { LayoutDashboard, Ticket, LogOut, ChevronRight, Settings, HelpCircle, Sun, Moon, Brain, Menu, X } from 'lucide-react';

export default function Navbar() {
    const { user, logout, darkMode, toggleTheme } = useAuth();
    const [isOpen, setIsOpen] = React.useState(false);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <>
            {/* Mobile Burger Button */}
            <button
                onClick={() => setIsOpen(true)}
                className="lg:hidden fixed top-6 left-6 z-[60] p-3 bg-brand-600 text-white rounded-2xl shadow-xl shadow-brand-500/30 active:scale-95 transition-all"
            >
                <Menu size={24} />
            </button>

            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    onClick={() => setIsOpen(false)}
                    className="lg:hidden fixed inset-0 bg-surface-900/60 backdrop-blur-sm z-[55] transition-all"
                ></div>
            )}

            <nav className={`fixed top-0 left-0 h-screen w-72 bg-white dark:bg-surface-900 border-r border-surface-200 dark:border-white/5 p-8 flex flex-col z-[56] shadow-2xl print:hidden transition-all duration-500 ease-in-out lg:translate-x-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                <div className="flex items-center justify-between mb-12">
                    <div className="flex items-center space-x-3 px-2">
                        <div className="w-10 h-10 bg-brand-600 rounded-2xl flex items-center justify-center shadow-lg shadow-brand-500/20">
                            <div className="w-5 h-5 bg-white rounded-full"></div>
                        </div>
                        <div>
                            <h1 className="text-2xl font-black text-surface-900 dark:text-white italic tracking-tighter leading-none">Syntivra</h1>
                            <p className="text-[10px] uppercase font-black tracking-[0.2em] text-surface-500 mt-1">Hub {user?.role === 'CUSTOMER' ? 'Cliente' : 'Unit'}</p>
                        </div>
                    </div>
                    <button onClick={() => setIsOpen(false)} className="lg:hidden p-2 text-surface-400 hover:text-surface-900">
                        <X size={20} />
                    </button>
                </div>

                <div className="flex-1 space-y-6">
                    <div className="space-y-1">
                        <p className="px-4 text-[10px] font-black uppercase tracking-widest text-surface-400 dark:text-surface-500 mb-2">Workspace</p>
                        {user?.role !== 'CUSTOMER' && (
                            <NavItem to="/" icon={<LayoutDashboard size={20} />} label="Visão Geral" />
                        )}
                        <NavItem to="/tickets" icon={<Ticket size={20} />} label={user?.role === 'CUSTOMER' ? 'Meus Chamados' : 'Atendimentos'} />
                    </div>

                    {user?.role !== 'CUSTOMER' && (
                        <div className="space-y-1">
                            <p className="px-4 text-[10px] font-black uppercase tracking-widest text-surface-400 dark:text-surface-500 mb-2">Gerenciamento</p>
                            <NavItem to="/ai-training" icon={<Brain size={20} />} label="Treinamento IA" />
                            <NavItem to="/settings" icon={<Settings size={20} />} label="Configurações" />
                            <NavItem to="/help" icon={<HelpCircle size={20} />} label="Central de Ajuda" />
                        </div>
                    )}
                </div>

                <div className="pt-8 border-t border-surface-200 dark:border-white/5 space-y-2">
                    <div className="bg-surface-50 dark:bg-surface-800/50 p-5 rounded-3xl border border-surface-200 dark:border-white/5 group transition-all hover:bg-surface-100 dark:hover:bg-surface-800 mb-4">
                        <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 rounded-2xl bg-brand-500 flex items-center justify-center text-white font-black text-xl border-4 border-white dark:border-surface-900 shadow-lg shadow-brand-500/20">
                                {user?.first_name?.[0]?.toUpperCase() || 'U'}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-black text-surface-900 dark:text-white truncate uppercase italic leading-none">{user?.first_name || 'Usuário'}</p>
                                <div className="flex items-center mt-1">
                                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>
                                    <p className="text-[10px] text-surface-500 dark:text-surface-400 font-bold uppercase truncate tracking-tighter">{user?.role}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={toggleTheme}
                        className="w-full flex items-center justify-between p-4 mb-2 text-surface-500 dark:text-surface-400 bg-surface-50 dark:bg-surface-800/30 hover:bg-surface-100 dark:hover:bg-surface-800 rounded-2xl transition-all border border-transparent dark:border-white/5"
                    >
                        <div className="flex items-center space-x-3">
                            {darkMode ? <Sun size={20} className="text-amber-500" /> : <Moon size={20} className="text-brand-500" />}
                            <span className="font-bold text-sm text-surface-900 dark:text-white">{darkMode ? 'Modo Claro' : 'Modo Escuro'}</span>
                        </div>
                    </button>

                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center justify-between p-4 text-surface-500 hover:bg-red-50 dark:hover:bg-red-900/10 hover:text-red-600 rounded-2xl transition-all group"
                    >
                        <div className="flex items-center space-x-3">
                            <LogOut size={20} />
                            <span className="font-bold text-sm">Sair do Sistema</span>
                        </div>
                    </button>
                </div>
            </nav>
        </>
    );
}

function NavItem({ to, icon, label }) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `flex items-center justify-between p-4 rounded-2xl transition-all font-bold group ${isActive
                    ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20 translate-x-1 outline outline-4 outline-brand-500/10'
                    : 'text-surface-500 dark:text-surface-400 hover:bg-surface-50 dark:hover:bg-white/5 hover:text-brand-500 dark:hover:text-white'
                }`
            }
        >
            {({ isActive }) => (
                <>
                    <div className="flex items-center space-x-4">
                        {icon}
                        <span className="text-sm">{label}</span>
                    </div>
                    <ChevronRight
                        size={16}
                        className={`transition-all ${isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-40'}`}
                    />
                </>
            )}
        </NavLink>
    );
}
