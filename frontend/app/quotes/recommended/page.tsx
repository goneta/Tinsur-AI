'use client';

import { useTranslation } from 'next-i18next';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CurrencyDisplay } from '@/components/CurrencyDisplay';
import QuoteDetailsModal from '@/components/modals/QuoteDetailsModal';
import axios from 'axios';

interface Quote {
  id: string;
  policy_name: string;
  premium: number;
  policy_id: string;
  vehicle_id: string;
  auto_generated: boolean;
  recommendation_order: number;
}

export default function RecommendedQuotesPage() {
  const { t } = useTranslation(['quotes', 'common']);
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const clientId = searchParams.get('client_id');
  
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!clientId) {
      router.push('/quotes/create');
      return;
    }

    const fetchRecommendedQuotes = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.post(
          `/api/v1/quotes/auto-generate/${clientId}`
        );
        
        if (response.data.recommended_quotes) {
          setQuotes(response.data.recommended_quotes);
        }
      } catch (error) {
        console.error('Failed to fetch quotes:', error);
        const errorMessage = 
          axios.isAxiosError(error) && error.response?.data?.detail
            ? error.response.data.detail
            : t('common:error_loading_quotes');
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendedQuotes();
  }, [clientId, router, t]);

  if (loading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">{t('common:loading')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800 mb-2">
            {t('common:error')}
          </h2>
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={() => router.push('/quotes/create')}
            className="btn btn-primary"
          >
            {t('quotes:create_custom_quote')}
          </button>
        </div>
      </div>
    );
  }

  if (quotes.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-yellow-800 mb-2">
            {t('quotes:no_quotes_found')}
          </h2>
          <p className="text-yellow-700 mb-4">
            {t('quotes:no_quotes_message')}
          </p>
          <button
            onClick={() => router.push('/quotes/create')}
            className="btn btn-primary"
          >
            {t('quotes:create_custom_quote')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">
          {t('quotes:recommended_quotes')}
        </h1>
        <p className="text-gray-600">
          {t('quotes:recommended_subtitle', {
            count: quotes.length,
          })}
        </p>
      </div>

      {/* Quotes List */}
      <div className="space-y-4">
        {quotes.map((quote, index) => (
          <div
            key={quote.id}
            className={`
              border rounded-lg p-6 hover:shadow-lg transition
              ${index === 0 ? 'border-green-400 bg-green-50' : 'border-gray-200'}
            `}
          >
            {/* Badge for cheapest option */}
            {index === 0 && (
              <div className="flex justify-end mb-3">
                <span className="inline-block px-3 py-1 text-sm font-semibold text-white bg-green-600 rounded-full">
                  ⭐ {t('quotes:cheapest')}
                </span>
              </div>
            )}

            {/* Quote Content */}
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-semibold">
                  {index + 1}. {quote.policy_name}
                </h2>
                <p className="text-gray-600 mt-1">
                  {t(`quotes:coverage_${quote.policy_name.toLowerCase()}`)}
                </p>
              </div>
              <div className="text-right">
                <CurrencyDisplay
                  amount={quote.premium}
                  size="large"
                  className="text-3xl font-bold text-green-600"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 pt-4 border-t border-gray-200">
              <button
                onClick={() => setSelectedQuote(quote)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition"
              >
                {t('quotes:view_details')}
              </button>
              <button
                onClick={() => {
                  router.push(`/quotes/${quote.id}/confirm`);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition"
              >
                {t('quotes:select_quote')}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Custom Quote */}
      <div className="mt-12 pt-8 border-t border-gray-200">
        <h3 className="text-lg font-semibold mb-4">
          {t('quotes:prefer_custom_quote')}
        </h3>
        <button
          onClick={() => router.push('/quotes/create')}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition"
        >
          {t('quotes:create_custom_quote')}
        </button>
      </div>

      {/* Quote Details Modal */}
      {selectedQuote && (
        <QuoteDetailsModal
          quote={selectedQuote}
          onClose={() => setSelectedQuote(null)}
          onSelect={() => {
            router.push(`/quotes/${selectedQuote.id}/confirm`);
            setSelectedQuote(null);
          }}
        />
      )}
    </div>
  );
}
