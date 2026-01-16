'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent } from '@/components/ui/card';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';

import { useAuth } from '@/lib/auth';

export type SharingScope = 'B2B' | 'B2C' | 'B2E' | 'E2E' | 'E2C' | 'C2C' | 'C2B' | 'C2E' | 'E2B';
export type ReshareRule = 'A' | 'B' | 'C';

export interface SharingConfig {
    visibility: 'PUBLIC' | 'PRIVATE';
    scope?: SharingScope;
    isShareable: boolean;
    reshareRule?: ReshareRule;
}

interface SharingSettingsProps {
    initialConfig?: Partial<SharingConfig>;
    onChange: (config: SharingConfig) => void;
}

export function SharingSettings({ initialConfig, onChange }: SharingSettingsProps) {
    const { user } = useAuth();
    const [visibility, setVisibility] = useState<'PUBLIC' | 'PRIVATE'>(initialConfig?.visibility || 'PRIVATE');
    const [scope, setScope] = useState<SharingScope>(initialConfig?.scope || 'B2B');
    const [isShareable, setIsShareable] = useState(initialConfig?.isShareable || false);
    const [reshareRule, setReshareRule] = useState<ReshareRule>(initialConfig?.reshareRule || 'C');

    const updateConfig = (
        v: 'PUBLIC' | 'PRIVATE',
        s: SharingScope,
        share: boolean,
        rule: ReshareRule
    ) => {
        onChange({
            visibility: v,
            scope: v === 'PRIVATE' ? s : undefined,
            isShareable: share,
            reshareRule: share ? rule : undefined
        });
    };

    const handleVisibilityChange = (val: 'PUBLIC' | 'PRIVATE') => {
        setVisibility(val);
        updateConfig(val, scope, isShareable, reshareRule);
    };

    const handleScopeChange = (val: SharingScope) => {
        setScope(val);
        updateConfig(visibility, val, isShareable, reshareRule);
    };

    // Logic: Option 1 (Not Shareable) -> isShareable=False
    // Option 2 (Shareable) -> isShareable=True
    const handleOptionChange = (val: '1' | '2') => {
        const share = val === '2';
        setIsShareable(share);
        updateConfig(visibility, scope, share, reshareRule);
    };

    const handleRuleChange = (val: ReshareRule) => {
        setReshareRule(val);
        updateConfig(visibility, scope, isShareable, val);
    };

    // Determine available scopes based on User Role
    const getAvailableScopes = (): SharingScope[] => {
        if (!user) return ['B2B']; // Default fallback

        const role = user.role;

        if (role === 'client') {
            return ['C2C', 'C2E', 'C2B'];
        }

        if (role === 'agent') { // Employee/Agent
            return ['E2C', 'E2E', 'E2B'];
        }

        if (role === 'company_admin' || role === 'manager' || role === 'super_admin') {
            return ['B2C', 'B2E', 'B2B'];
        }

        return ['B2B']; // Fallback
    };

    const availableScopes = getAvailableScopes();

    // Ensure selected scope is valid for the current role
    // This effect runs when user or scope changes
    // If the current scope is NOT in the allowed list, switch to the first allowed one.
    // However, we should be careful about infinite loops or overwriting initial props unnecessarily.
    // For now, let's just render the allowed ones. If existing selection is invalid, it will show but maybe we should force update?
    // Let's just filter the list for now.

    return (
        <div className="space-y-6">
            {/* Visibility */}
            <div className="space-y-3">
                <Label className="text-base">Visibility</Label>
                <RadioGroup value={visibility} onValueChange={(v) => handleVisibilityChange(v as any)} className="flex gap-4">
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="PUBLIC" id="pub" />
                        <Label htmlFor="pub">Public (All Users)</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="PRIVATE" id="priv" />
                        <Label htmlFor="priv">Private</Label>
                    </div>
                </RadioGroup>
            </div>

            {visibility === 'PRIVATE' && (
                <div className="space-y-6 pl-4 border-l-2 border-primary/20">
                    {/* Scope */}
                    <div className="space-y-3">
                        <Label>Sharing Scope</Label>
                        <Select value={scope} onValueChange={(v) => handleScopeChange(v as any)}>
                            <SelectTrigger className="w-[280px]">
                                <SelectValue placeholder="Select Scope" />
                            </SelectTrigger>
                            <SelectContent>
                                {availableScopes.includes('B2B') && <SelectItem value="B2B">B2B (Business to Business)</SelectItem>}
                                {availableScopes.includes('B2C') && <SelectItem value="B2C">B2C (Business to Client)</SelectItem>}
                                {availableScopes.includes('B2E') && <SelectItem value="B2E">B2E (Business to Employee)</SelectItem>}
                                {availableScopes.includes('E2E') && <SelectItem value="E2E">E2E (Employee to Employee)</SelectItem>}
                                {availableScopes.includes('E2C') && <SelectItem value="E2C">E2C (Employee to Client)</SelectItem>}
                                {availableScopes.includes('E2B') && <SelectItem value="E2B">E2B (Employee to Business)</SelectItem>}
                                {availableScopes.includes('C2C') && <SelectItem value="C2C">C2C (Client to Client)</SelectItem>}
                                {availableScopes.includes('C2B') && <SelectItem value="C2B">C2B (Client to Business)</SelectItem>}
                                {availableScopes.includes('C2E') && <SelectItem value="C2E">C2E (Client to Employee)</SelectItem>}
                            </SelectContent>
                        </Select>
                        <p className="text-xs text-muted-foreground">
                            {scope === 'B2B' && "Clients do not have access."}
                            {scope === 'B2C' && "Other companies do not have access."}
                            {scope === 'B2E' && "Clients and other companies excluded."}
                        </p>
                    </div>

                    {/* Sharing Options */}
                    <div className="space-y-3">
                        <Label>Sharing Options</Label>
                        <RadioGroup value={isShareable ? '2' : '1'} onValueChange={(v) => handleOptionChange(v as any)}>
                            <div className="flex items-center space-x-2">
                                <RadioGroupItem value="1" id="opt1" />
                                <Label htmlFor="opt1">Option 1: Not Shareable</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <RadioGroupItem value="2" id="opt2" />
                                <Label htmlFor="opt2">Option 2: Shareable</Label>
                            </div>
                        </RadioGroup>
                    </div>

                    {/* Reshare Rules (Only if Shareable) */}
                    {isShareable && (
                        <div className="space-y-3 pl-4 pt-2">
                            <Label>Reshare Permission (Rule)</Label>
                            <RadioGroup value={reshareRule} onValueChange={(v) => handleRuleChange(v as any)}>
                                <div className="flex items-center space-x-2">
                                    <RadioGroupItem value="A" id="ruleA" />
                                    <Label htmlFor="ruleA">A: Can share with others who can re-share</Label>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <RadioGroupItem value="B" id="ruleB" />
                                    <Label htmlFor="ruleB">B: Can share, but recipient CANNOT re-share</Label>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <RadioGroupItem value="C" id="ruleC" />
                                    <Label htmlFor="ruleC">C: Cannot share with others (Owner Only)</Label>
                                </div>
                            </RadioGroup>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
