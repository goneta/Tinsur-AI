'use client';

import { useTranslation } from 'next-i18next';
import { useState, useEffect } from 'react';
import { CurrencyDisplay } from '@/components/CurrencyDisplay';
import axios from 'axios';

interface QuoteDetailsModalProps {
  quote: {
    id: string;
    policy_name: string;
    premium: number;
    policy_id: string;
    vehicle_id: string;
  };
  onClose: () => void;
  onSelect: () => void;
}

interface QuoteDetails {
  id: string;
  premium: number;
  policy_name: string;
  deductible: number;
  coverage: {
    third_party: boolean;
    collision: boolean;
    theft: boolean;
  };
  benefits: string[];
  discounts: string[];
}

export default function QuoteDetailsModal({
  quote,
  onClose,
  onSelect,
}: QuoteDetailsModalProps) {
  const { t } = useTranslation(['quotes', 'common']);
  const [activeTab, setActiveTab] = useState('overview');
  const [details, setDetails] = useState<QuoteDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await axios.get(`/api/v1/quotes/${quote.id}/details`);
        
        if (response.data.details) {
          setDetails(response.data.details);
        }
      } catch (error) {
        console.error('Failed to fetch quote details:', error);
        setError(t('common:error_loading_details'));
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [quote.id, t]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">{t('common:loading')}</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-2xl font-bold">{quote.policy_name}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ✕
            </button>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 font-medium"
          >
            {t('common:close')}
          </button>
        </div>
      </div>
    );
  }

  if (!details) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-start">
          <div>
            <h2 className="text-3xl font-bold">{details.policy_name}</h2>
            <p className="text-gray-600 mt-1">
              {t(`quotes:coverage_${details.policy_name.toLowerCase()}`)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-3xl leading-none"
          >
            ✕
          </button>
        </div>

        {/* Premium Highlight */}
        <div className="bg-blue-50 p-6 border-b">
          <div className="flex justify-between items-center">
            <span className="text-gray-700 font-semibold">
              {t('quotes:annual_premium')}
            </span>
            <CurrencyDisplay
              amount={details.premium}
              size="large"
              className="text-3xl font-bold text-blue-600"
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b bg-gray-50 sticky top-20">
          {['overview', 'coverage', 'benefits'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-6 py-4 font-semibold transition ${
                activeTab === tab
                  ? 'border-b-2 border-blue-600 text-blue-600 bg-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {t(`quotes:tab_${tab}`)}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Deductible */}
              <div className="border rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 font-semibold">
                    {t('quotes:deductible')}
                  </span>
                  <CurrencyDisplay amount={details.deductible} size="medium" />
                </div>
              </div>

              {/* Premium */}
              <div className="border rounded-lg p-4 bg-blue-50">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 font-semibold">
                    {t('quotes:premium_amount')}
                  </span>
                  <CurrencyDisplay
                    amount={details.premium}
                    size="medium"
                    className="text-blue-600"
                  />
                </div>
              </div>

              {/* Description */}
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700">
                  {t(
                    `quotes:description_${details.policy_name.toLowerCase()}`
                  )}
                </p>
              </div>

              {/* Quick Benefits */}
              <div className="border rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-3">
                  {t('quotes:key_benefits')}
                </h4>
                <ul className="space-y-2">
                  {details.benefits.slice(0, 2).map((benefit, idx) => (
                    <li key={idx} className="flex items-center text-gray-700">
                      <span className="text-green-600 mr-2 text-lg">✓</span>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Coverage Tab */}
          {activeTab === 'coverage' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-6">
                {t('quotes:included_coverage')}
              </h3>

              <div className="space-y-3">
                {/* Third Party */}
                <div className="border rounded-lg p-4 flex items-start">
                  <span
                    className={`text-2xl mr-4 ${
                      details.coverage.third_party
                        ? 'text-green-600'
                        : 'text-gray-300'
                    }`}
                  >
                    ✓
                  </span>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800">
                      {t('quotes:coverage_third_party')}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {t('quotes:coverage_third_party_desc')}
                    </p>
                  </div>
                </div>

                {/* Collision */}
                <div className="border rounded-lg p-4 flex items-start">
                  <span
                    className={`text-2xl mr-4 ${
                      details.coverage.collision
                        ? 'text-green-600'
                        : 'text-gray-300'
                    }`}
                  >
                    ✓
                  </span>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800">
                      {t('quotes:coverage_collision')}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {t('quotes:coverage_collision_desc')}
                    </p>
                  </div>
                </div>

                {/* Theft */}
                <div className="border rounded-lg p-4 flex items-start">
                  <span
                    className={`text-2xl mr-4 ${
                      details.coverage.theft ? 'text-green-600' : 'text-gray-300'
                    }`}
                  >
                    ✓
                  </span>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800">
                      {t('quotes:coverage_theft')}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {t('quotes:coverage_theft_desc')}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Benefits Tab */}
          {activeTab === 'benefits' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-6">
                {t('quotes:included_benefits')}
              </h3>

              <div className="space-y-3">
                {details.benefits.map((benefit, idx) => (
                  <div
                    key={idx}
                    className="border rounded-lg p-4 flex items-start bg-blue-50"
                  >
                    <span className="text-2xl mr-4 text-blue-600">★</span>
                    <div className="flex-1">
                      <p className="text-gray-800 font-semibold">{benefit}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Discounts */}
              {details.discounts && details.discounts.length > 0 && (
                <div className="mt-8 pt-8 border-t">
                  <h4 className="font-semibold text-gray-800 mb-4">
                    {t('quotes:available_discounts')}
                  </h4>
                  <div className="space-y-2">
                    {details.discounts.map((discount, idx) => (
                      <div
                        key={idx}
                        className="flex items-center text-green-700 bg-green-50 p-3 rounded-lg"
                      >
                        <span className="mr-2">💰</span>
                        {discount}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="sticky bottom-0 bg-white border-t p-6 flex gap-4">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 font-semibold transition"
          >
            {t('common:close')}
          </button>
          <button
            onClick={onSelect}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition"
          >
            {t('quotes:select_this_quote')}
          </button>
        </div>
      </div>
    </div>
  );
}
