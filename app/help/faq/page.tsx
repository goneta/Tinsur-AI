'use client';

import { useState } from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const faqs = [
  {
    category: 'Getting Started',
    items: [
      {
        question: 'How do I create my first account?',
        answer:
          'Visit the sign-up page and enter your email, name, and password. You\'ll receive a verification email. Click the link to activate your account.',
      },
      {
        question: 'Do I need technical skills to use Tinsur-AI?',
        answer:
          'No! Tinsur-AI is designed to be user-friendly. We provide comprehensive guides and tutorials to help you get started.',
      },
      {
        question: 'What are the system requirements?',
        answer:
          'You need a modern web browser (Chrome, Firefox, Safari, or Edge) and a reliable internet connection. No software installation is required.',
      },
    ],
  },
  {
    category: 'Clients & Quotes',
    items: [
      {
        question: 'How do I add a new client?',
        answer:
          'Go to Clients → Add New Client. Fill in their basic information and click Save. You can add more details later.',
      },
      {
        question: 'How long does it take to generate a quote?',
        answer:
          'Our AI-powered system generates quotes in seconds. The exact time depends on the complexity of the coverage options.',
      },
      {
        question: 'Can I customize quotes after they\'re generated?',
        answer:
          'Yes! You can adjust deductibles, coverage limits, and add optional riders before sending to the client.',
      },
      {
        question: 'How long are quotes valid for?',
        answer:
          'By default, quotes are valid for 30 days. You can customize the expiration date when creating a quote.',
      },
    ],
  },
  {
    category: 'Policies & Claims',
    items: [
      {
        question: 'How do I track policy renewals?',
        answer:
          'Go to Policies and filter by "Expiring Soon". The system sends automatic reminders 30, 14, and 7 days before expiration.',
      },
      {
        question: 'Can I manage claims in Tinsur-AI?',
        answer:
          'Yes! The Claims section allows you to log, track, and manage insurance claims. You can attach documents and track the status.',
      },
      {
        question: 'How do I export policy information?',
        answer:
          'Go to Reports → Policy Report. Select your filters and click "Export as CSV" or "Export as PDF".',
      },
    ],
  },
  {
    category: 'Team & Administration',
    items: [
      {
        question: 'How many users can I add to my account?',
        answer:
          'There\'s no limit on the number of users. Add as many team members as you need to your organization.',
      },
      {
        question: 'What are the different user roles?',
        answer:
          'Admin (full access), Manager (create clients and approve quotes), Agent (manage assigned clients), and Viewer (read-only access).',
      },
      {
        question: 'How do I enable two-factor authentication?',
        answer:
          'Go to Settings → Security → Two-Factor Authentication. Follow the setup wizard to configure 2FA with your preferred authenticator app.',
      },
      {
        question: 'Can I deactivate a user without deleting them?',
        answer:
          'Yes! Go to Team Management, find the user, and click "Deactivate". They won\'t have access but their data remains intact.',
      },
    ],
  },
  {
    category: 'Security & Data',
    items: [
      {
        question: 'Is my data secure?',
        answer:
          'Yes. We use TLS 1.2+ encryption in transit and AES-256 encryption at rest. We also comply with GDPR, ISO 27001, and SOC 2 Type II standards.',
      },
      {
        question: 'Can I export my data?',
        answer:
          'Yes! You can export data in CSV or PDF format from the Reports section. You can also request a full data export from Settings.',
      },
      {
        question: 'How often is my data backed up?',
        answer:
          'Your data is automatically backed up daily. We maintain multiple backup copies for disaster recovery.',
      },
      {
        question: 'What happens if I forget my password?',
        answer:
          'Click "Forgot Password" on the login page. You\'ll receive an email with a reset link. Click it and create a new password.',
      },
    ],
  },
  {
    category: 'Billing & Support',
    items: [
      {
        question: 'What payment methods do you accept?',
        answer:
          'We accept credit cards (Visa, MasterCard, American Express), bank transfers, and other local payment methods depending on your region.',
      },
      {
        question: 'Can I change my subscription plan?',
        answer:
          'Yes! Go to Settings → Billing to upgrade or downgrade your plan. Changes take effect immediately.',
      },
      {
        question: 'How do I contact support?',
        answer:
          'You can email support@tinsur-ai.com, use the in-app chat support, or post on our community forum at community.tinsur-ai.com.',
      },
      {
        question: 'What are your support hours?',
        answer:
          'Email support is available 24/7. Live chat support is available Monday to Friday, 9 AM to 5 PM GMT.',
      },
    ],
  },
];

export default function FAQPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [openItem, setOpenItem] = useState<string | null>(null);

  const filteredFaqs = searchQuery
    ? faqs.map((category) => ({
        ...category,
        items: category.items.filter(
          (item) =>
            item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.answer.toLowerCase().includes(searchQuery.toLowerCase())
        ),
      }))
    : faqs;

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">Frequently Asked Questions</h1>
        <p className="text-lg text-muted-foreground">
          Find answers to common questions about Tinsur-AI
        </p>
      </div>

      {/* Search */}
      <Input
        type="search"
        placeholder="Search FAQ..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="h-10"
      />

      {/* FAQ Categories */}
      <div className="space-y-8">
        {filteredFaqs.map((category) => (
          category.items.length > 0 && (
            <div key={category.category} className="space-y-4">
              <h2 className="text-2xl font-bold">{category.category}</h2>
              <Accordion
                type="single"
                collapsible
                value={openItem || ''}
                onValueChange={setOpenItem}
              >
                {category.items.map((item, index) => (
                  <AccordionItem
                    key={`${category.category}-${index}`}
                    value={`${category.category}-${index}`}
                  >
                    <AccordionTrigger className="text-left hover:no-underline hover:text-primary">
                      {item.question}
                    </AccordionTrigger>
                    <AccordionContent className="text-base pt-4">
                      {item.answer}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>
          )
        ))}

        {filteredFaqs.every((cat) => cat.items.length === 0) && (
          <Card>
            <CardContent className="pt-6 text-center text-muted-foreground">
              No FAQ items found matching "{searchQuery}"
            </CardContent>
          </Card>
        )}
      </div>

      {/* Contact */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle>Didn't find what you were looking for?</CardTitle>
          <CardDescription>
            Contact our support team for personalized help
          </CardDescription>
        </CardHeader>
        <CardContent>
          <a href="mailto:support@tinsur-ai.com" className="text-primary hover:underline">
            → Email us at support@tinsur-ai.com
          </a>
        </CardContent>
      </Card>
    </div>
  );
}
