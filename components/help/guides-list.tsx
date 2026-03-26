'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Clock, Check, ArrowRight } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useDebounce } from '@/hooks/use-debounce';

interface Guide {
  id: string;
  title: string;
  description: string;
  guide_type: string;
  section?: string;
  estimated_read_time: number;
  tags?: string[];
}

interface GuidesListProps {
  guides: Guide[];
  completedGuides?: string[];
  onSearch?: (query: string) => void;
  loading?: boolean;
}

export function GuidesList({
  guides,
  completedGuides = [],
  onSearch,
  loading = false,
}: GuidesListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearch = useDebounce(searchQuery, 300);

  useEffect(() => {
    if (onSearch) {
      onSearch(debouncedSearch);
    }
  }, [debouncedSearch, onSearch]);

  const getRoleBadgeColor = (guideType: string) => {
    switch (guideType) {
      case 'client':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'admin':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'insurance_company':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const guideTypeLabel = (type: string) => {
    return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 w-1/3 bg-muted rounded" />
              <div className="h-3 w-1/2 bg-muted rounded mt-2" />
            </CardHeader>
            <CardContent>
              <div className="h-3 w-full bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      {onSearch && (
        <div className="relative">
          <Input
            type="search"
            placeholder="Search guides..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
          <span className="absolute left-3 top-3 text-muted-foreground">🔍</span>
        </div>
      )}

      {/* Guides Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {guides.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="pt-6 text-center text-muted-foreground">
              {searchQuery ? 'No guides found matching your search.' : 'No guides available.'}
            </CardContent>
          </Card>
        ) : (
          guides.map((guide) => {
            const isCompleted = completedGuides.includes(guide.id);
            return (
              <Link key={guide.id} href={`/help/guides/${guide.id}`}>
                <Card className="h-full transition-all hover:shadow-lg hover:border-primary cursor-pointer">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 space-y-2">
                        <CardTitle className="text-lg">{guide.title}</CardTitle>
                        <CardDescription className="text-xs">
                          {guide.description}
                        </CardDescription>
                      </div>
                      {isCompleted && (
                        <Check className="h-5 w-5 text-green-600 mt-1 flex-shrink-0" />
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1">
                      <Badge className={`text-xs ${getRoleBadgeColor(guide.guide_type)}`}>
                        {guideTypeLabel(guide.guide_type)}
                      </Badge>
                      {guide.section && (
                        <Badge variant="outline" className="text-xs">
                          {guide.section.replace(/_/g, ' ')}
                        </Badge>
                      )}
                      {guide.tags?.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    {/* Read Time */}
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{guide.estimated_read_time} min read</span>
                      </div>
                      <ArrowRight className="h-4 w-4" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })
        )}
      </div>
    </div>
  );
}
