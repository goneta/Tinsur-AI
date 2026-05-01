
'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useLanguage } from '@/contexts/language-context';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog';
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { User, UserCreate, UserUpdate } from '@/types/user';
import { Loader2 } from 'lucide-react';

const userSchema = z.object({
    email: z.string().email(),
    first_name: z.string().min(2, "First name is required"),
    last_name: z.string().min(2, "Last name is required"),
    role: z.string(),
    password: z.string().min(8, "Password must be at least 8 characters").optional().or(z.literal('')),
    phone: z.string().optional(),
});

type UserFormValues = z.infer<typeof userSchema>;

interface UserDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    user: User | null;
    onSave: (data: any) => Promise<void>;
}

export function UserDialog({ open, onOpenChange, user, onSave }: UserDialogProps) {
    const { t } = useLanguage();
    const form = useForm<UserFormValues>({
        resolver: zodResolver(userSchema),
        defaultValues: {
            email: '',
            first_name: '',
            last_name: '',
            role: 'agent',
            password: '',
            phone: '',
        },
    });

    useEffect(() => {
        if (user) {
            form.reset({
                email: user.email,
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                role: user.role,
                phone: user.phone || '',
                password: '', // Don't show password
            });
        } else {
            form.reset({
                email: '',
                first_name: '',
                last_name: '',
                role: 'agent',
                password: '',
                phone: '',
            });
        }
    }, [user, form, open]);

    const onSubmit = async (data: UserFormValues) => {
        // If editing, exclude password if empty
        const submissionData = { ...data };
        if (user && !submissionData.password) {
            delete submissionData.password;
        }
        await onSave(submissionData);
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>{user ? 'Edit User' : 'Create New User'}</DialogTitle>
                    <DialogDescription>
                        {user ? 'Update user details and role assignment.' : 'Add a new user to the organization.'}
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="first_name"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>First Name</FormLabel>
                                        <FormControl>
                                            <Input placeholder={t('placeholder.enter_name', 'Enter name')} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="last_name"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Last Name</FormLabel>
                                        <FormControl>
                                            <Input placeholder={t('placeholder.enter_name', 'Enter name')} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <FormField
                            control={form.control}
                            name="email"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Email</FormLabel>
                                    <FormControl>
                                        <Input placeholder="john@example.com" {...field} disabled={!!user} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="phone"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Phone</FormLabel>
                                    <FormControl>
                                        <Input placeholder="+1 555 000 0000" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="role"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Role</FormLabel>
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder={t('placeholder.select_role', 'Select a role')} />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="company_admin">Company Admin</SelectItem>
                                            <SelectItem value="manager">Manager</SelectItem>
                                            <SelectItem value="agent">Agent</SelectItem>
                                            <SelectItem value="employee">Employee</SelectItem>
                                            <SelectItem value="client">Client</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {(!user || user) && ( // Always allow password reset capability if needed, or hide on edit
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>{user ? 'New Password (Optional)' : 'Password'}</FormLabel>
                                        <FormControl>
                                            <Input type="password" placeholder={user ? "Leave blank to keep current" : "Secure password"} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        )}

                        <DialogFooter>
                            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>{t('btn.cancel', 'Cancel')}</Button>
                            <Button type="submit" disabled={form.formState.isSubmitting}>
                                {form.formState.isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                {user ? t('btn.save_changes', 'Save Changes') : t('btn.create_user', 'Create User')}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
