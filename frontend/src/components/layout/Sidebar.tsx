import { useState } from "react";
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
  ChevronDown,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { getActiveBrand, setActiveBrand } from "@/lib/brand";

const BRANDS = [
  { id: "acme-corp", name: "Acme Corp" },
  { id: "nike", name: "Nike" },
  { id: "aws", name: "AWS" },
];

const navItems = [
  { label: "Dashboard",   icon: LayoutDashboard, href: "/dashboard"   },
  { label: "Monitoring",  icon: Radar,            href: "/monitoring"  },
  { label: "Graph",       icon: GitFork,          href: "/graph"       },
  { label: "Threats",     icon: AlertTriangle,    href: "/threats"     },
  { label: "Corrections", icon: CheckCircle,      href: "/corrections" },
  { label: "Agent",       icon: Bot,              href: "/agent"       },
  { label: "Settings",    icon: Settings,         href: "/settings"    },
];

export default function Sidebar() {
  const location = useLocation();
  const [activeBrand, setActive] = useState(getActiveBrand());

  function handleBrandChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const id = e.target.value;
    setActiveBrand(id);
    setActive(id);
    window.location.reload();
  }

  const brandLabel = BRANDS.find((b) => b.id === activeBrand)?.name ?? activeBrand;

  return (
    <aside className="hidden md:flex w-64 flex-col border-r bg-sidebar">
      <div className="flex h-14 items-center border-b px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <Shield className="h-5 w-5" />
          <span>BrandGuard</span>
        </Link>
      </div>

      {/* Brand selector */}
      <div className="px-4 pt-4 pb-2">
        <label className="text-xs font-medium text-sidebar-foreground/60 uppercase tracking-wider">
          Active Brand
        </label>
        <div className="relative mt-1">
          <select
            value={activeBrand}
            onChange={handleBrandChange}
            className="w-full appearance-none rounded-lg border bg-sidebar-accent px-3 py-2 pr-8 text-sm font-medium text-sidebar-accent-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
          >
            {BRANDS.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-sidebar-foreground/50" />
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            to={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
              location.pathname === item.href
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
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
