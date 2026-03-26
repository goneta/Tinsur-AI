'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BookOpen, MessageSquare, Search, Zap } from 'lucide-react';
import { GuidesList } from '@/components/help/guides-list';

interface Guide {
  id: string;
  title: string;
  description: string;
  guide_type: string;
  section?: string;
  estimated_read_time: number;
  tags?: string[];
}

export default function HelpPage() {
  const [guides, setGuides] = useState<Guide[]>([]);
  const [filteredGuides, setFilteredGuides] = useState<Guide[]>([]);
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [completedGuides, setCompletedGuides] = useState<string[]>([]);

  useEffect(() => {
    loadGuides();
    loadCompletionStatus();
  }, []);

  useEffect(() => {
    filterGuides();
  }, [guides, activeTab, searchQuery]);

  const loadGuides = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/help/guides');
      if (response.ok) {
        const data = await response.json();
        setGuides(data);
      }
    } catch (error) {
      console.error('Failed to load guides:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCompletionStatus = async () => {
    try {
      const response = await fetch('/api/v1/help/completion-status');
      if (response.ok) {
        const data = await response.json();
        setCompletedGuides(data.completed_guides || []);
      }
    } catch (error) {
      console.error('Failed to load completion status:', error);
    }
  };

  const filterGuides = () => {
    let filtered = guides;

    // Filter by type
    if (activeTab !== 'all') {
      filtered = filtered.filter((g) => g.guide_type === activeTab);
    }

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((g) =>
        g.title.toLowerCase().includes(query) ||
        g.description.toLowerCase().includes(query) ||
        g.tags?.some((t) => t.toLowerCase().includes(query))
      );
    }

    setFilteredGuides(filtered);
  };

  const handleSearch = async (query: string) => {
    if (query.trim().length > 0) {
      try {
        const response = await fetch(`/api/v1/help/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
          const data = await response.json();
          setFilteredGuides(data);
        }
      } catch (error) {
        console.error('Search failed:', error);
      }
    } else {
      setSearchQuery('');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Help & Documentation</h1>
          <p className="text-lg text-muted-foreground mt-2">
            Learn how to use Tinsur-AI with our comprehensive guides and tutorials
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-3 sm:grid-cols-3">
          <Link href="/help/get-started">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <Zap className="h-6 w-6 text-blue-500 mb-2" />
                <p className="font-semibold text-sm">Get Started</p>
                <p className="text-xs text-muted-foreground mt-1">
                  New to Tinsur-AI? Start here
                </p>
              </CardContent>
            </Card>
          </Link>

          <a href="mailto:support@tinsur-ai.com">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <MessageSquare className="h-6 w-6 text-green-500 mb-2" />
                <p className="font-semibold text-sm">Get Support</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Contact our support team
                </p>
              </CardContent>
            </Card>
          </a>

          <Link href="/help/faq">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <BookOpen className="h-6 w-6 text-orange-500 mb-2" />
                <p className="font-semibold text-sm">FAQ</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Common questions answered
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>

      {/* Guides */}
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold mb-4">Browse Guides</h2>

          {/* Tabs and Search */}
          <div className="space-y-4">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="all">All Guides</TabsTrigger>
                <TabsTrigger value="client">For Clients</TabsTrigger>
                <TabsTrigger value="admin">For Admins</TabsTrigger>
                <TabsTrigger value="insurance_company">For Companies</TabsTrigger>
              </TabsList>

              {/* Search is above tabs content */}
            </Tabs>

            <Input
              type="search"
              placeholder="Search guides..."
              onChange={(e) => handleSearch(e.target.value)}
              className="h-10"
            />
          </div>
        </div>

        {/* Guides List */}
        <GuidesList
          guides={filteredGuides}
          completedGuides={completedGuides}
          loading={loading}
        />
      </div>
    </div>
  );
}
