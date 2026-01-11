import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// Theme Types
type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    // Initialize from localStorage or default to 'light'
    try {
      const saved = localStorage.getItem('finq_theme');
      if (saved === 'dark' || saved === 'light') {
        return saved;
      }
    } catch (e) {
      console.error('Error reading theme from localStorage:', e);
    }
    return 'light';
  });

  useEffect(() => {
    // Apply theme class to HTML element
    const root = document.documentElement;

    // Tailwind uses only 'dark' class for dark mode
    // Light mode = no class
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Persist to localStorage
    try {
      localStorage.setItem('finq_theme', theme);
    } catch (e) {
      console.error('Error saving theme to localStorage:', e);
    }

    console.log('Theme applied:', theme, 'Dark class present:', root.classList.contains('dark'));
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => {
      const newTheme = prev === 'light' ? 'dark' : 'light';
      console.log('Toggling theme from', prev, 'to', newTheme);
      return newTheme;
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
