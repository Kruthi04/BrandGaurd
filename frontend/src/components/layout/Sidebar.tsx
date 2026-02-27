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

const navItems = [
  { label: "Dashboard",   icon: LayoutDashboard, href: "/"            },
  { label: "Monitoring",  icon: Radar,            href: "/monitoring"  },
  { label: "Graph",       icon: GitFork,          href: "/graph"       },
  { label: "Threats",     icon: AlertTriangle,    href: "/threats"     },
  { label: "Corrections", icon: CheckCircle,      href: "/corrections" },
  { label: "Agent",       icon: Bot,              href: "/agent"       },
  { label: "Settings",    icon: Settings,         href: "/settings"    },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="hidden md:flex w-64 flex-col border-r bg-sidebar">
      <div className="flex h-14 items-center border-b px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <Shield className="h-5 w-5" />
          <span>BrandGuard</span>
        </Link>
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
