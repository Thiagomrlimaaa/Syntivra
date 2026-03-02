import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/useAuth';

// Layout
import Navbar from './components/Layout/Navbar';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import TicketList from './pages/TicketList';
import TicketDetail from './pages/TicketDetail';
import Settings from './pages/Settings';
import AITraining from './pages/AITraining';

const PrivateRoute = ({ children }) => {
    const { user, token, darkMode } = useAuth();
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className={`flex min-h-screen transition-colors duration-500 ${darkMode ? 'dark bg-[#020617]' : 'bg-surface-50'}`}>
            <Navbar />
            <div className={`flex-1 transition-all duration-300 ml-0 lg:ml-72 print:ml-0 min-h-screen`}>
                <main className="p-6 lg:p-10 max-w-7xl mx-auto w-full print:p-0 print:max-w-none">
                    {children}
                </main>
            </div>
        </div>
    );
};

// Componente para decidir a Home baseada no Role
const Home = () => {
    const user = useAuth(state => state.user);
    if (user?.role === 'CUSTOMER') {
        return <Navigate to="/tickets" replace />;
    }
    return <Dashboard />;
};

function App() {
    const init = useAuth(state => state.init);

    useEffect(() => {
        init();
    }, [init]);

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />

                <Route path="/" element={
                    <PrivateRoute>
                        <Home />
                    </PrivateRoute>
                } />

                <Route path="/tickets" element={
                    <PrivateRoute>
                        <TicketList />
                    </PrivateRoute>
                } />

                <Route path="/tickets/:id" element={
                    <PrivateRoute>
                        <TicketDetail />
                    </PrivateRoute>
                } />

                <Route path="/settings" element={
                    <PrivateRoute>
                        <Settings />
                    </PrivateRoute>
                } />

                <Route path="/ai-training" element={
                    <PrivateRoute>
                        <AITraining />
                    </PrivateRoute>
                } />

                {/* Fallback para rotas não encontradas */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
