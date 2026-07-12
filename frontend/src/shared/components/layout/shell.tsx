import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  ChevronRight,
  LayoutDashboard,
  Leaf,
  LogOut,
  Menu,
  Moon,
  Shield,
  Sun,
  Trophy,
  Users,
  X,
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";

import { useAuth } from "@/modules/auth/hooks/useAuth";
import { usePermission } from "@/modules/auth/hooks/usePermission";
import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Separator } from "@/shared/components/ui/separator";
import { APP_NAME } from "@/shared/constants/app";
import { useTheme } from "@/shared/hooks/use-theme";
import { cn } from "@/shared/lib/utils";

const navigationItems = [
  { label: "Dashboard", path: "/", permission: "dashboard:read", icon: LayoutDashboard },
  { label: "Environmental", path: "/environmental", permission: "carbon:read", icon: Leaf },
  { label: "Social", path: "/social", permission: "csr:read", icon: Users },
  { label: "Governance", path: "/governance", permission: "policies:read", icon: Shield },
  { label: "Gamification", path: "/gamification", permission: "challenges:read", icon: Trophy },
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
    if (item.permission === "dashboard:read") return hasDashboardRead;
    if (item.permission === "carbon:read") return hasCarbonRead;
    if (item.permission === "csr:read") return hasCsrRead;
    if (item.permission === "policies:read") return hasPoliciesRead;
    if (item.permission === "challenges:read") return hasChallengesRead;
    return true;
  });
}

function NavItems({ onNavigate, compact }: { onNavigate?: () => void; compact?: boolean }) {
  const visibleItems = useVisibleNavItems();

  return (
    <>
      <p
        className={cn(
          "px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground",
          compact ? "mb-2" : "mb-3",
        )}
      >
        Modules
      </p>
      {visibleItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
              isActive
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
            )
          }
        >
          {({ isActive }) => (
            <>
              <item.icon
                className={cn("h-4 w-4 shrink-0", isActive ? "text-primary-foreground" : "text-primary")}
                aria-hidden
              />
              <span>{item.label}</span>
            </>
          )}
        </NavLink>
      ))}
    </>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r bg-card md:flex">
      <div className="flex h-16 items-center gap-2.5 border-b px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
          <Leaf className="h-5 w-5 text-primary" aria-hidden />
        </div>
        <span className="text-lg font-semibold tracking-tight">{APP_NAME}</span>
      </div>
      <nav className="scrollbar-thin flex flex-1 flex-col gap-1 overflow-y-auto p-4">
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
      <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b bg-card/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-card/80 md:px-6">
        <div className="flex min-w-0 items-center gap-3">
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
          <div className="min-w-0">
            <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-xs text-muted-foreground">
              <span>EcoSphere</span>
              <ChevronRight className="h-3 w-3 shrink-0" aria-hidden />
              <span className="truncate font-medium text-foreground">{pageTitle}</span>
            </nav>
            <h1 className="truncate text-lg font-semibold tracking-tight">{pageTitle}</h1>
          </div>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          >
            {theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </Button>
          <Separator orientation="vertical" className="hidden h-6 sm:block" />
          <div className="flex items-center gap-2 sm:gap-3">
            <Avatar className="h-9 w-9 border">
              <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="hidden text-right lg:block">
              <p className="max-w-[10rem] truncate text-sm font-medium">{displayName}</p>
              <div className="flex justify-end gap-1">
                {user?.roles.slice(0, 2).map((role) => (
                  <Badge key={role.id} variant="secondary" className="text-[10px]">
                    {role.name}
                  </Badge>
                ))}
              </div>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => void logout()}
              aria-label="Logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>
      <AnimatePresence>
        {mobileNavOpen ? (
          <motion.nav
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden border-b bg-card md:hidden"
            aria-label="Mobile navigation"
          >
            <div className="scrollbar-thin max-h-[60vh] overflow-y-auto p-4">
              <NavItems compact onNavigate={() => setMobileNavOpen(false)} />
            </div>
          </motion.nav>
        ) : null}
      </AnimatePresence>
    </>
  );
}
