'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { HelpCircle, BookOpen, MessageSquare, LifeBuoy, KeyboardShortcuts, ExternalLink } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface HelpButtonProps {
  className?: string;
  contextPage?: string;
}

export function HelpButton({ className, contextPage }: HelpButtonProps) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  const contextGuides: Record<string, string> = {
    'clients': 'client-management',
    'quotes': 'quote-creation',
    'policies': 'policy-management',
    'reports': 'reports',
    'admin': 'user-management',
    'settings': 'security',
  };

  const guideId = contextPage ? contextGuides[contextPage] : undefined;

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className={className}
          title="Get help"
        >
          <HelpCircle className="h-5 w-5" />
          <span className="sr-only">Help</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="flex items-center gap-2">
          <HelpCircle className="h-4 w-4" />
          Help & Resources
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuGroup>
          <DropdownMenuLabel className="text-xs font-normal text-muted-foreground py-1.5">
            Documentation
          </DropdownMenuLabel>

          <DropdownMenuItem asChild>
            <Link href="/help/guides" className="cursor-pointer">
              <BookOpen className="mr-2 h-4 w-4" />
              <span>All Guides</span>
            </Link>
          </DropdownMenuItem>

          <DropdownMenuItem asChild>
            <Link href="/help/get-started" className="cursor-pointer">
              <LifeBuoy className="mr-2 h-4 w-4" />
              <span>Get Started</span>
            </Link>
          </DropdownMenuItem>

          {guideId && (
            <DropdownMenuItem asChild>
              <Link href={`/help/guides/${guideId}`} className="cursor-pointer">
                <HelpCircle className="mr-2 h-4 w-4" />
                <span>Help for this page</span>
              </Link>
            </DropdownMenuItem>
          )}
        </DropdownMenuGroup>

        <DropdownMenuSeparator />

        <DropdownMenuGroup>
          <DropdownMenuLabel className="text-xs font-normal text-muted-foreground py-1.5">
            Support
          </DropdownMenuLabel>

          <DropdownMenuItem asChild>
            <a
              href="mailto:support@tinsur-ai.com"
              className="cursor-pointer"
            >
              <MessageSquare className="mr-2 h-4 w-4" />
              <span>Contact Support</span>
            </a>
          </DropdownMenuItem>

          <DropdownMenuItem asChild>
            <a
              href="/help/faq"
              className="cursor-pointer"
            >
              <BookOpen className="mr-2 h-4 w-4" />
              <span>FAQ</span>
            </a>
          </DropdownMenuItem>
        </DropdownMenuGroup>

        <DropdownMenuSeparator />

        <DropdownMenuGroup>
          <DropdownMenuLabel className="text-xs font-normal text-muted-foreground py-1.5">
            Other
          </DropdownMenuLabel>

          <DropdownMenuItem asChild>
            <a
              href="/help/keyboard-shortcuts"
              className="cursor-pointer"
            >
              <KeyboardShortcuts className="mr-2 h-4 w-4" />
              <span>Keyboard Shortcuts</span>
            </a>
          </DropdownMenuItem>

          <DropdownMenuItem asChild>
            <a
              href="https://community.tinsur-ai.com"
              target="_blank"
              rel="noopener noreferrer"
              className="cursor-pointer"
            >
              <ExternalLink className="mr-2 h-4 w-4" />
              <span>Community Forum</span>
            </a>
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
