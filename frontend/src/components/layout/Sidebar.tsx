import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Radar,
  GitFork,
  AlertTriangle,
  CheckCircle,
  Bot,
  Settings,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useActiveBrand, setActiveBrand } from "@/lib/brand";
import { useQueryClient } from "@tanstack/react-query";

const navItems = [
  { label: "Dashboard",   icon: LayoutDashboard, href: "/dashboard"   },
  { label: "Monitoring",  icon: Radar,            href: "/monitoring"  },
  { label: "Graph",       icon: GitFork,          href: "/graph"       },
  { label: "Threats",     icon: AlertTriangle,    href: "/threats"     },
  { label: "Corrections", icon: CheckCircle,      href: "/corrections" },
  { label: "Agent",       icon: Bot,              href: "/agent"       },
  { label: "Settings",    icon: Settings,         href: "/settings"    },
];

const BRANDS = [
  { id: "yutori",         label: "Yutori" },
  { id: "neo4j",          label: "Neo4j" },
  { id: "senso",          label: "Senso" },
  { id: "render",         label: "Render" },
  { id: "tavily",         label: "Tavily" },
];

export default function Sidebar() {
  const location = useLocation();
  const queryClient = useQueryClient();
  const activeBrand = useActiveBrand();

  function handleBrandChange(e: React.ChangeEvent<HTMLSelectElement>) {
    setActiveBrand(e.target.value);
    queryClient.invalidateQueries();
  }

  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="flex h-14 items-center border-b border-sidebar-border px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold text-sidebar-primary-foreground">
          <Shield className="h-5 w-5 text-blue-400" />
          <span>BrandGuard</span>
        </Link>
      </div>

      {/* Brand Switcher */}
      <div className="px-4 pt-4 pb-2">
        <label className="text-xs font-medium text-muted-foreground mb-1 block">Active Brand</label>
        <select
          className="w-full rounded-md border bg-background px-2 py-1.5 text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          value={activeBrand}
          onChange={handleBrandChange}
        >
          {BRANDS.map((b) => (
            <option key={b.id} value={b.id}>{b.label}</option>
          ))}
        </select>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            to={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
              location.pathname === item.href
                ? "bg-blue-500/15 text-blue-400 font-medium"
                : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
