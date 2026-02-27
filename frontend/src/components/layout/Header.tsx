import { Shield } from "lucide-react";
import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <Shield className="h-5 w-5" />
          <span>BrandGuard</span>
        </Link>
        <nav className="ml-8 flex items-center gap-6 text-sm">
          <Link to="/" className="text-muted-foreground hover:text-foreground transition-colors">
            Dashboard
          </Link>
          <Link to="/monitoring" className="text-muted-foreground hover:text-foreground transition-colors">
            Monitoring
          </Link>
          <Link to="/graph" className="text-muted-foreground hover:text-foreground transition-colors">
            Graph
          </Link>
          <Link to="/threats" className="text-muted-foreground hover:text-foreground transition-colors">
            Threats
          </Link>
          <Link to="/agent" className="text-muted-foreground hover:text-foreground transition-colors">
            Agent
          </Link>
          <Link to="/settings" className="text-muted-foreground hover:text-foreground transition-colors">
            Settings
          </Link>
        </nav>
      </div>
    </header>
  );
}
