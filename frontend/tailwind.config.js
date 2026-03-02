/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    50: '#eff6ff',
                    100: '#dbeafe',
                    200: '#bfdbfe',
                    300: '#93c5fd',
                    400: '#60a5fa',
                    500: '#2563EB', // Azul Principal
                    600: '#1D4ED8', // Azul Hover
                    700: '#1d4ed8',
                    800: '#1e40af',
                    900: '#1e3a8a',
                    950: '#172554',
                },
                surface: {
                    50: '#F8FAFC',  // Background
                    100: '#F1F5F9',
                    200: '#E2E8F0', // Border
                    300: '#CBD5E1',
                    400: '#94A3B8',
                    500: '#64748B', // Secondary Text
                    600: '#475569',
                    700: '#334155',
                    800: '#1E293B',
                    900: '#0F172A', // Sidebar / Titles
                    950: '#020617',
                }
            },
            backgroundImage: {
                'gradient-premium': 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
                'dark-mesh': 'radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.15) 0, transparent 50%), radial-gradient(at 50% 0%, rgba(139, 92, 246, 0.15) 0, transparent 50%), radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.15) 0, transparent 50%)',
            },
            animation: {
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'float': 'float 6s ease-in-out infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            boxShadow: {
                'premium': '0 10px 40px -10px rgba(0, 0, 0, 0.05)',
                'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07)',
            },
            borderRadius: {
                '2xl': '1.25rem',
                '3xl': '1.5rem',
            }
        },
    },
    plugins: [],
}
