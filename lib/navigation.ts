import {
    LayoutDashboard,
    Users,
    FileText,
    Calculator,
    Shield,
    CreditCard,
    BarChart3,
    Settings,
    LucideIcon,
    AlertCircle,
    LifeBuoy,
    Share2,
    Activity,
    Heart,
    Bot,
    UserPlus,
    Users2,
    CircleDollarSign,
    Store,
    Coins,
    BookOpen,
    Gavel,
    Landmark,
    Database,
    HelpCircle,
} from 'lucide-react';

export interface NavItem {
    id: string;
    title: string;
    href: string;
    icon: LucideIcon;
    roles?: string[]; // If undefined, accessible by all authenticated users
    color?: string; // Base color for the icon background and text (e.g., 'blue', 'green')
    items?: NavItem[];
}

export interface NavGroup {
    id: string;
    title: string;
    items: NavItem[];
}

export const clientNavItems: NavItem[] = [
    {
        id: 'dashboard',
        title: 'Dashboard',
        href: '/portal',
        icon: LayoutDashboard,
    },
    {
        id: 'my_policies',
        title: 'My Policies',
        href: '/portal/policies',
        icon: Shield,
    },
    {
        id: 'my_claims',
        title: 'My Claims',
        href: '/portal/claims',
        icon: AlertCircle,
    },
    {
        id: 'payments',
        title: 'Payments',
        href: '/portal/payments',
        icon: CreditCard,
    },
    {
        id: 'settings',
        title: 'Settings',
        href: '/portal/settings',
        icon: Settings,
    },
];

export const navGroups: NavGroup[] = [
    {
        id: 'overview',
        title: "Overview",
        items: [
            {
                id: 'dashboard',
                title: 'Dashboard',
                href: '/dashboard',
                icon: LayoutDashboard,
                color: 'blue',
            },
            {
                id: 'analytics',
                title: "Analytics",
                href: "/dashboard/analytics",
                icon: BarChart3,
                roles: ["super_admin", "company_admin"],
                color: 'amber',
            }
        ]
    },
    {
        id: 'operations',
        title: "Operations",
        items: [
            {
                id: 'quote',
                title: 'Quotes',
                href: '/dashboard/quotes',
                icon: Calculator,
                color: 'orange',
            },
            {
                id: 'policy',
                title: 'Policies',
                href: '/dashboard/policies',
                icon: Shield,
                color: 'indigo',
            },
            {
                id: 'claims',
                title: 'Claims',
                href: '/dashboard/claims',
                icon: AlertCircle,
                color: 'red',
            },
            {
                id: 'clients',
                title: 'Clients',
                href: '/dashboard/clients',
                icon: Users,
                color: 'green',
            },
            {
                id: 'tickets',
                title: 'Support Tickets',
                href: '/dashboard/support',
                icon: LifeBuoy,
                color: 'pink',
            },
            {
                id: 'import_export',
                title: 'Import / Export Data',
                href: '/dashboard/import-export',
                icon: Database,
                color: 'blue',
            }
        ]
    },
    {
        id: 'finance',
        title: "Finance",
        items: [
            {
                id: 'payments',
                title: 'Payments',
                href: '/dashboard/payments',
                icon: CreditCard,
                color: 'purple',
            },
            {
                id: 'accounting',
                title: "Accounting",
                href: "/dashboard/financials",
                icon: BookOpen,
                roles: ["super_admin", "company_admin", "accountant"],
                color: 'blue',
            },
            {
                id: 'regulatory',
                title: "Executive Financials",
                href: "/dashboard/financials/regulatory",
                icon: Landmark,
                roles: ["super_admin", "company_admin", "manager"],
                color: 'indigo',
            },
            {
                id: 'commissions',
                title: 'Commissions',
                href: '/dashboard/commissions',
                icon: Coins,
                roles: ["super_admin", "company_admin", "manager", "agent"],
                color: 'amber',
            },
            {
                id: 'financial_reports',
                title: 'Financial Reports',
                href: '/dashboard/analytics?tab=finance',
                icon: BarChart3,
                roles: ['admin', 'manager', 'company_admin'],
                color: 'amber',
            },
        ]
    },
    {
        id: 'management',
        title: "Management",
        items: [
            {
                id: 'decisions',
                title: 'Decision Hub',
                href: '/dashboard/decisions',
                icon: Gavel,
                roles: ['super_admin', 'company_admin', 'manager'],
                color: 'blue',
            },
            {
                id: 'employees',
                title: 'Employees',
                href: '/dashboard/employees',
                icon: Users2,
                roles: ['super_admin', 'company_admin', 'manager'],
                color: 'teal',
            },
            {
                id: 'payroll',
                title: 'Payroll',
                href: '/dashboard/payroll',
                icon: CircleDollarSign,
                roles: ['super_admin', 'company_admin', 'manager'],
                color: 'emerald',
            },
            {
                id: 'templates',
                title: 'Policy Templates',
                href: '/dashboard/policy-templates',
                icon: FileText,
                roles: ['super_admin', 'company_admin', 'manager', 'admin'],
                color: 'cyan',
            },
            {
                id: 'policy_types',
                title: 'Policy Types',
                href: '/dashboard/policy-types',
                icon: Shield,
                roles: ['super_admin', 'company_admin', 'manager', 'admin'],
                color: 'violet',
            },
            {
                id: 'pos',
                title: 'POS Management',
                href: '/dashboard/pos',
                icon: Store,
                roles: ['super_admin', 'company_admin', 'manager'],
                color: 'slate',
            },
            {
                id: 'settings',
                title: 'Settings',
                href: '/dashboard/settings',
                icon: Settings,
                roles: ['super_admin', 'company_admin'],
                color: 'slate',
            },

            {
                id: 'premium_policies',
                title: 'Premium Policies',
                href: '/dashboard/admin/premium-policies',
                icon: Shield,
                roles: ['super_admin', 'company_admin'],
                color: 'amber',
            },
            {
                id: 'services',
                title: 'Policy Services',
                href: '/dashboard/admin/services',
                icon: Shield,
                roles: ['super_admin', 'company_admin'],
                color: 'blue',
            },
            {
                id: 'admin',
                title: 'Admin',
                href: '/dashboard/admin',
                icon: Shield,
                roles: ['super_admin', 'company_admin'],
                color: 'red',
            },
        ]
    },
    {
        id: 'tools',
        title: "Tools",
        items: [
            {
                id: 'ai_manager',
                title: 'AI Agent Manager',
                href: '/dashboard/ai-manager',
                icon: Bot,
                roles: ['super_admin', 'company_admin', 'manager', 'agent'],
                color: 'indigo',
            },
            {
                id: 'collaboration',
                title: 'Collaboration',
                href: '/dashboard/collaboration',
                icon: Share2,
                roles: ['super_admin', 'company_admin', 'manager'],
                color: 'violet',
            },
            {
                id: 'loyalty',
                title: 'Loyalty Program',
                href: '/dashboard/loyalty',
                icon: Heart,
                roles: ['super_admin', 'company_admin'],
                color: 'rose',
            },
            {
                id: 'telematics',
                title: 'Telematics',
                href: '/dashboard/telematics',
                icon: Activity,
                roles: ['super_admin', 'company_admin', 'agent'],
                color: 'cyan',
            },
            {
                id: 'help_guides',
                title: 'Help & Guides',
                href: '/help/guides',
                icon: HelpCircle,
                color: 'blue',
            },
        ]
    }
];

export function getNavGroupsForRole(role?: string): NavGroup[] {
    if (!role) return [];

    return navGroups.map(group => ({
        id: group.id,
        title: group.title,
        items: group.items.filter(item => {
            if (!item.roles) return true;
            return item.roles.includes(role) || item.roles.includes(role.toLowerCase());
        })
    })).filter(group => group.items.length > 0);
}
