import { create } from 'zustand';
import { jwtDecode } from 'jwt-decode';

export const useAuth = create((set) => ({
    user: null,
    token: localStorage.getItem('token') || null,

    setToken: (token) => {
        localStorage.setItem('token', token);
        const decoded = jwtDecode(token);
        set({ token, user: decoded });
    },

    logout: () => {
        localStorage.removeItem('token');
        set({ token: null, user: null });
    },

    darkMode: localStorage.getItem('theme') === 'dark',

    toggleTheme: () => {
        set((state) => {
            const nextMode = !state.darkMode;
            const theme = nextMode ? 'dark' : 'light';
            localStorage.setItem('theme', theme);
            if (nextMode) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
            return { darkMode: nextMode };
        });
    },

    init: () => {
        const token = localStorage.getItem('token');
        const theme = localStorage.getItem('theme') || 'light';

        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }

        if (token) {
            try {
                const decoded = jwtDecode(token);
                set({ token, user: decoded, darkMode: theme === 'dark' });
            } catch (e) {
                localStorage.removeItem('token');
                set({ darkMode: theme === 'dark' });
            }
        } else {
            set({ darkMode: theme === 'dark' });
        }
    }
}));
