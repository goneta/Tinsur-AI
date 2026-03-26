import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Help & Documentation | Tinsur.AI',
  description: 'Comprehensive guides, tutorials, and documentation for Tinsur.AI',
};

export default function HelpLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        {children}
      </main>
    </div>
  );
}
