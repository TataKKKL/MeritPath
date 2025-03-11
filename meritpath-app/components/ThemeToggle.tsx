import { useTheme } from "next-themes";
import { HiSun, HiMoon } from "react-icons/hi";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch by only rendering after component is mounted
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="p-2 rounded-md hover:bg-foreground/5"
      aria-label="Toggle theme"
    >
      {theme === "dark" ? (
        <HiSun className="w-5 h-5" />
      ) : (
        <HiMoon className="w-5 h-5" />
      )}
    </button>
  );
} 