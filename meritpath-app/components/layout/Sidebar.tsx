import Link from "next/link";
import { useRouter } from "next/router";
import ThemeToggle from "../ThemeToggle";

export default function Sidebar() {
  const router = useRouter();
  
  const isActive = (path: string) => {
    return router.pathname === path ? "bg-foreground/10" : "";
  };

  return (
    <div className="w-64 h-full border-r border-foreground/10 bg-background">
      <div className="p-4 border-b border-foreground/10 flex justify-between items-center">
        <h1 className="text-xl font-bold">MeritPath</h1>
        <ThemeToggle />
      </div>
      
      <nav className="p-2">
        <ul className="space-y-1">
          <li>
            <Link href="/" className={`flex items-center px-4 py-2 rounded-md hover:bg-foreground/5 ${isActive("/")}`}>
              <span className="mr-3">🏠</span>
              <span>Home</span>
            </Link>
          </li>
          <li>
            <Link href="/dashboard" className={`flex items-center px-4 py-2 rounded-md hover:bg-foreground/5 ${isActive("/dashboard")}`}>
              <span className="mr-3">📊</span>
              <span>All Your Citers</span>
            </Link>
          </li>
          <li>
            <Link href="/citers" className={`flex items-center px-4 py-2 rounded-md hover:bg-foreground/5 ${isActive("/citers")}`}>
              <span className="mr-3">📊</span>
              <span>Shortlist Potential Citers</span>
            </Link>
          </li>
          <li>
            <Link href="/final" className={`flex items-center px-4 py-2 rounded-md hover:bg-foreground/5 ${isActive("/final")}`}>
              <span className="mr-3">📊</span>
              <span>Finalize Your Citers</span>
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  );
} 