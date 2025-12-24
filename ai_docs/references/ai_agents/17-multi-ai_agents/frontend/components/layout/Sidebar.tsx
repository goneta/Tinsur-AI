"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  CreditCard,
  Target,
  TrendingUp,
  Gift,
  Users,
  User,
  LogOut,
  Brain,
  DollarSign,
} from "lucide-react";
import { useAuth } from "@/components/auth/AuthContext";
import { Button } from "@/components/ui/button";

const navigationItems = [
  {
    name: "Spending",
    href: "/spending",
    icon: CreditCard,
  },
  // {
  //   name: "Goals",
  //   href: "/goals",
  //   icon: Target,
  // },
  {
    name: "Portfolio",
    href: "/portfolio",
    icon: TrendingUp,
  },
  {
    name: "Perks",
    href: "/perks",
    icon: Gift,
  },
  {
    name: "Advisors",
    href: "/advisors",
    icon: Users,
  },
  // {
  //   name: "Profile",
  //   href: "/profile",
  //   icon: User,
  // },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout(); // This sets user context to null
    router.push("/"); // Redirect to login page
  };

  return (
    <div className="w-64 bg-background/95 backdrop-blur-md border-r border-border/50 flex flex-col relative">
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-primary/5 pointer-events-none" />

      {/* Header with FI Logo */}
      <div className="relative p-6 border-b border-border/30">
        <div className="flex items-center gap-3 group">
          {/* Mini FI Logo */}
          <div className="relative">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-cyan-500 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-primary/25 transition-all duration-300">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div className="absolute -top-0.5 -right-0.5">
              <DollarSign className="h-3.5 w-3.5 text-cyan-400" />
            </div>
          </div>

          {/* Brand Text */}
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-cyan-600 bg-clip-text text-transparent">
              FI
            </h1>
            <p className="text-xs text-muted-foreground">
              Financial Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 group relative overflow-hidden
                    ${
                      isActive
                        ? "bg-gradient-to-r from-primary/10 to-cyan-500/10 text-primary border border-primary/20 shadow-sm"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                    }
                  `}
                >
                  {/* Active indicator */}
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-primary to-cyan-500 rounded-r-full" />
                  )}

                  <Icon
                    className={`w-5 h-5 mr-3 transition-colors duration-200 ${
                      isActive ? "text-primary" : "group-hover:text-primary"
                    }`}
                  />

                  <span className="relative z-10">{item.name}</span>

                  {/* Hover effect background */}
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-xl" />
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Enhanced User Info & Logout */}
      <div className="relative p-4 border-t border-border/30">
        {user && (
          <div className="space-y-4">
            {/* User Profile Card */}
            <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-xl p-4 shadow-sm">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-background flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-white rounded-full" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-foreground truncate">
                    {user.username}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Active Session
                  </p>
                </div>
              </div>
            </div>

            {/* Logout Button */}
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start bg-background/50 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30 transition-all duration-200"
              onClick={handleLogout}
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
