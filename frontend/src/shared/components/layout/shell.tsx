import { useState } from "react";
import { Leaf, LogOut, Menu, Moon, Sun, X } from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";

import { useAuth } from "@/modules/auth/hooks/useAuth";
import { usePermission } from "@/modules/auth/hooks/usePermission";
import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Separator } from "@/shared/components/ui/separator";
import { APP_NAME } from "@/shared/constants/app";
import { useTheme } from "@/shared/hooks/use-theme";

const navigationItems = [
  { label: "Dashboard", path: "/", permission: "dashboard:read" },
  { label: "Environmental", path: "/environmental", permission: "carbon:read" },
  { label: "Social", path: "/social", permission: "csr:read" },
  { label: "Governance", path: "/governance", permission: "policies:read" },
  { label: "Gamification", path: "/gamification", permission: "challenges:read" },
];

const pageTitles: Record<string, string> = {
  "/": "Executive Dashboard",
  "/environmental": "Environmental Dashboard",
  "/social": "Social Dashboard",
  "/governance": "Governance Dashboard",
  "/gamification": "Gamification Dashboard",
};

function getInitials(firstName?: string, lastName?: string, email?: string): string {
  if (firstName && lastName) {
    return `${firstName[0]}${lastName[0]}`.toUpperCase();
  }
  return email?.slice(0, 2).toUpperCase() ?? "ES";
}

function useVisibleNavItems() {
  const hasDashboardRead = usePermission("dashboard:read");
  const hasCarbonRead = usePermission("carbon:read");
  const hasCsrRead = usePermission("csr:read");
  const hasPoliciesRead = usePermission("policies:read");
  const hasChallengesRead = usePermission("challenges:read");

  return navigationItems.filter((item) => {
    if (!item.permission) return true;
    if (item.permission === "dashboard:read") return hasDashboardRead;
    if (item.permission === "carbon:read") return hasCarbonRead;
    if (item.permission === "csr:read") return hasCsrRead;
    if (item.permission === "policies:read") return hasPoliciesRead;
    if (item.permission === "challenges:read") return hasChallengesRead;
    return true;
  });
}

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  const visibleItems = useVisibleNavItems();

  return (
    <>
      {visibleItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          onClick={onNavigate}
          className={({ isActive }) =>
            `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col border-r bg-card md:flex">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <Leaf className="h-6 w-6 text-primary" />
        <span className="text-lg font-semibold">{APP_NAME}</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-4">
        <NavItems />
      </nav>
    </aside>
  );
}

export function Topbar() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const displayName = user?.employee
    ? `${user.employee.first_name} ${user.employee.last_name}`
    : user?.email;

  const initials = getInitials(
    user?.employee?.first_name,
    user?.employee?.last_name,
    user?.email,
  );

  const pageTitle = pageTitles[location.pathname] ?? "EcoSphere";

  return (
    <>
      <header className="flex h-16 items-center justify-between border-b bg-card px-4 md:px-6">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileNavOpen((open) => !open)}
            aria-label={mobileNavOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={mobileNavOpen}
          >
            {mobileNavOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <div>
            <p className="text-sm text-muted-foreground">Enterprise ESG Platform</p>
            <h1 className="text-lg font-semibold">{pageTitle}</h1>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </Button>
          <Separator orientation="vertical" className="hidden h-6 sm:block" />
          <div className="flex items-center gap-3">
            <Avatar>
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium">{displayName}</p>
              <div className="flex justify-end gap-1">
                {user?.roles.map((role) => (
                  <Badge key={role.id} variant="secondary">
                    {role.name}
                  </Badge>
                ))}
              </div>
            </div>
            <Button variant="outline" size="icon" onClick={() => void logout()} aria-label="Logout">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>
      {mobileNavOpen ? (
        <nav
          className="flex flex-col gap-1 border-b bg-card p-4 md:hidden"
          aria-label="Mobile navigation"
        >
          <NavItems onNavigate={() => setMobileNavOpen(false)} />
        </nav>
      ) : null}
    </>
  );
}
