/**
 * Delete Confirmation Modal - Usage Examples
 * 
 * Copy/paste these examples into your components
 */

'use client';

import React, { useState } from 'react';
import { useDeleteConfirmation } from '@/hooks/useDeleteConfirmation';
import { DeleteConfirmationModal } from '@/components/DeleteConfirmationModal';
import api from '@/lib/api';

/**
 * EXAMPLE 1: Delete Quote from List
 */
export function DeleteQuoteExample() {
  const [quotes, setQuotes] = useState<any[]>([
    { id: '1', number: 'QT-2026-001', client: 'Client A', amount: 5000 },
    { id: '2', number: 'QT-2026-002', client: 'Client B', amount: 7500 },
  ]);

  const { deleteState, showDeleteConfirmation, handleConfirm, handleCancel } =
    useDeleteConfirmation();

  const handleDeleteQuote = async (quoteId: string, quoteNumber: string) => {
    showDeleteConfirmation(
      quoteNumber,
      async () => {
        // Call API to delete
        await api.delete(`/quotes/${quoteId}`);
        
        // Remove from local state
        setQuotes(quotes.filter((q) => q.id !== quoteId));
      },
      {
        title: 'Delete Quote',
        message: `Delete quote "${quoteNumber}"? This action cannot be undone.`,
        confirmText: 'Delete Quote',
        isDangerous: true,
      }
    );
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Quotes</h2>

      <div className="space-y-2">
        {quotes.map((quote) => (
          <div
            key={quote.id}
            className="flex items-center justify-between rounded-lg border p-4"
          >
            <div>
              <p className="font-semibold">{quote.number}</p>
              <p className="text-sm text-gray-600">{quote.client}</p>
            </div>
            <button
              onClick={() =>
                handleDeleteQuote(quote.id, quote.number)
              }
              className="rounded bg-red-100 px-3 py-2 text-red-600 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      {/* Modal */}
      <DeleteConfirmationModal
        isOpen={deleteState.isOpen}
        title={deleteState.title}
        itemName={deleteState.itemName}
        message={deleteState.message}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        isLoading={deleteState.isLoading}
        isDangerous={deleteState.isDangerous}
      />
    </div>
  );
}

/**
 * EXAMPLE 2: Delete User Account
 */
export function DeleteUserAccountExample() {
  const [users, setUsers] = useState<any[]>([
    { id: '1', name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: '2', name: 'Jane Smith', email: 'jane@example.com', role: 'User' },
  ]);

  const { deleteState, showDeleteConfirmation, handleConfirm, handleCancel } =
    useDeleteConfirmation();

  const handleDeleteUser = async (userId: string, userName: string) => {
    showDeleteConfirmation(
      userName,
      async () => {
        await api.delete(`/users/${userId}`);
        setUsers(users.filter((u) => u.id !== userId));
      },
      {
        title: 'Delete User Account',
        message: `Are you sure you want to delete the account for "${userName}"? This will also delete all their associated data. This action cannot be undone.`,
        confirmText: 'Delete Account',
        cancelText: 'Keep Account',
        isDangerous: true,
      }
    );
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Users</h2>

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b">
            <th className="px-4 py-2 text-left">Name</th>
            <th className="px-4 py-2 text-left">Email</th>
            <th className="px-4 py-2 text-left">Role</th>
            <th className="px-4 py-2 text-center">Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="border-b">
              <td className="px-4 py-2">{user.name}</td>
              <td className="px-4 py-2">{user.email}</td>
              <td className="px-4 py-2">{user.role}</td>
              <td className="px-4 py-2 text-center">
                <button
                  onClick={() => handleDeleteUser(user.id, user.name)}
                  className="text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Modal */}
      <DeleteConfirmationModal
        isOpen={deleteState.isOpen}
        title={deleteState.title}
        itemName={deleteState.itemName}
        message={deleteState.message}
        confirmText={deleteState.confirmText}
        cancelText={deleteState.cancelText}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        isLoading={deleteState.isLoading}
        isDangerous={deleteState.isDangerous}
      />
    </div>
  );
}

/**
 * EXAMPLE 3: Delete from Card Component
 */
export function DeleteInsuranceProductExample() {
  const [products, setProducts] = useState<any[]>([
    { id: '1', name: 'Auto Insurance', coverage: 'Comprehensive' },
    { id: '2', name: 'Home Insurance', coverage: 'Standard' },
  ]);

  const { deleteState, showDeleteConfirmation, handleConfirm, handleCancel } =
    useDeleteConfirmation();

  const handleDeleteProduct = async (productId: string, productName: string) => {
    showDeleteConfirmation(
      productName,
      async () => {
        await api.delete(`/products/${productId}`);
        setProducts(products.filter((p) => p.id !== productId));
      },
      {
        title: 'Remove Insurance Product',
        message: `Remove "${productName}" from available products?`,
        confirmText: 'Remove Product',
        isDangerous: true,
      }
    );
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Insurance Products</h2>

      <div className="grid gap-4 md:grid-cols-2">
        {products.map((product) => (
          <div
            key={product.id}
            className="rounded-lg border border-gray-200 p-4"
          >
            <h3 className="font-semibold">{product.name}</h3>
            <p className="text-sm text-gray-600">{product.coverage}</p>

            <div className="mt-4 flex gap-2">
              <button className="flex-1 rounded bg-blue-100 px-3 py-2 text-blue-600">
                Edit
              </button>
              <button
                onClick={() =>
                  handleDeleteProduct(product.id, product.name)
                }
                className="flex-1 rounded bg-red-100 px-3 py-2 text-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      <DeleteConfirmationModal
        isOpen={deleteState.isOpen}
        title={deleteState.title}
        itemName={deleteState.itemName}
        message={deleteState.message}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        isLoading={deleteState.isLoading}
        isDangerous={deleteState.isDangerous}
      />
    </div>
  );
}

/**
 * EXAMPLE 4: Bulk Delete from Checkbox Selection
 */
export function BulkDeleteExample() {
  const [items, setItems] = useState<any[]>([
    { id: '1', name: 'Item 1' },
    { id: '2', name: 'Item 2' },
    { id: '3', name: 'Item 3' },
  ]);

  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const { deleteState, showDeleteConfirmation, handleConfirm, handleCancel } =
    useDeleteConfirmation();

  const handleBulkDelete = async () => {
    showDeleteConfirmation(
      `${selectedIds.length} items`,
      async () => {
        // Call API to delete multiple items
        await api.post('/items/delete-bulk', { ids: selectedIds });

        // Remove from local state
        setItems(items.filter((item) => !selectedIds.includes(item.id)));
        setSelectedIds([]);
      },
      {
        title: 'Delete Multiple Items',
        message: `Delete ${selectedIds.length} selected items? This action cannot be undone.`,
        confirmText: `Delete ${selectedIds.length} Items`,
        isDangerous: true,
      }
    );
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Items</h2>
        {selectedIds.length > 0 && (
          <button
            onClick={handleBulkDelete}
            className="rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700"
          >
            Delete Selected ({selectedIds.length})
          </button>
        )}
      </div>

      <div className="space-y-2">
        {items.map((item) => (
          <label
            key={item.id}
            className="flex items-center gap-3 rounded-lg border p-3 hover:bg-gray-50"
          >
            <input
              type="checkbox"
              checked={selectedIds.includes(item.id)}
              onChange={() => toggleSelect(item.id)}
              className="h-4 w-4"
            />
            <span>{item.name}</span>
          </label>
        ))}
      </div>

      {/* Modal */}
      <DeleteConfirmationModal
        isOpen={deleteState.isOpen}
        title={deleteState.title}
        itemName={deleteState.itemName}
        message={deleteState.message}
        confirmText={deleteState.confirmText}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        isLoading={deleteState.isLoading}
        isDangerous={deleteState.isDangerous}
      />
    </div>
  );
}
