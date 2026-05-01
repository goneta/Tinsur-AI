"use client";

import { useEffect, useMemo, useState } from "react";
import { tasksApi, Task } from "@/lib/tasks-api";
import { useLanguage } from "@/contexts/language-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { ClipboardList, Plus } from "lucide-react";

export default function TasksPage() {
    const { t } = useLanguage();
    const { toast } = useToast();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [employees, setEmployees] = useState<Array<{ id: string; first_name?: string; last_name?: string; email?: string }>>([]);
    const [employeesLoading, setEmployeesLoading] = useState(false);

    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [priority, setPriority] = useState<Task["priority"]>("medium");
    const [status, setStatus] = useState<Task["status"]>("pending");
    const [dueDate, setDueDate] = useState("");
    const [assignedTo, setAssignedTo] = useState("");

    const loadTasks = async () => {
        try {
            setLoading(true);
            const data = await tasksApi.listTasks();
            setTasks(data);
        } catch (error) {
            toast({
                title: t('common.error', 'Error'),
                description: t('tasks.load_failed', 'Failed to load tasks.'),
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTasks();
    }, []);

    useEffect(() => {
        const loadEmployees = async () => {
            try {
                setEmployeesLoading(true);
                const data = await tasksApi.listEmployees();
                setEmployees(data || []);
            } catch (error) {
                toast({
                    title: t('common.error', 'Error'),
                    description: t('tasks.load_employees_failed', 'Failed to load employees.'),
                    variant: "destructive",
                });
            } finally {
                setEmployeesLoading(false);
            }
        };
        loadEmployees();
    }, []);

    const employeeMap = useMemo(() => {
        const map = new Map<string, { id: string; first_name?: string; last_name?: string; email?: string }>();
        employees.forEach((emp) => map.set(emp.id, emp));
        return map;
    }, [employees]);

    const formatEmployeeLabel = (employee?: { first_name?: string; last_name?: string; email?: string }) => {
        if (!employee) return t('tasks.unassigned', 'Unassigned');
        const fullName = [employee.first_name, employee.last_name].filter(Boolean).join(" ").trim();
        return fullName || employee.email || t('tasks.unassigned', 'Unassigned');
    };

    const handleCreateTask = async () => {
        if (!title.trim()) {
            toast({
                title: t('tasks.missing_title', 'Missing title'),
                description: t('tasks.provide_title', 'Please provide a task title.'),
                variant: "destructive",
            });
            return;
        }
        try {
            setCreating(true);
            await tasksApi.createTask({
                title,
                description: description || undefined,
                priority,
                status,
                due_date: dueDate || undefined,
                assigned_to: assignedTo || undefined,
            });
            setTitle("");
            setDescription("");
            setPriority("medium");
            setStatus("pending");
            setDueDate("");
            setAssignedTo("");
            await loadTasks();
            toast({
                title: t('tasks.created', 'Task created'),
                description: t('tasks.created_desc', 'The task has been added successfully.'),
            });
        } catch (error) {
            toast({
                title: t('common.error', 'Error'),
                description: t('tasks.create_failed', 'Failed to create task.'),
                variant: "destructive",
            });
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="flex flex-col gap-6 p-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{t('tasks.title', 'Tasks')}</h1>
                    <p className="text-muted-foreground mt-2">
                        {t('tasks.subtitle', 'Track internal work items, follow-ups, and approvals.')}
                    </p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <ClipboardList className="h-4 w-4" /> {t('tasks.create_task', 'Create Task')}
                    </CardTitle>
                    <CardDescription>{t('tasks.add_for_team', 'Add a new task for your team.')}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>{t('common.title', 'Title')}</Label>
                            <Input value={title} onChange={(e) => setTitle(e.target.value)} />
                        </div>
                        <div className="space-y-2">
                            <Label>{t('tasks.assigned_to', 'Assigned To')}</Label>
                            <select
                                className="w-full border rounded-md px-3 py-2 text-sm bg-white"
                                value={assignedTo}
                                onChange={(e) => setAssignedTo(e.target.value)}
                                disabled={employeesLoading}
                            >
                                <option value="">{t('tasks.unassigned', 'Unassigned')}</option>
                                {employees.map((employee) => (
                                    <option key={employee.id} value={employee.id}>
                                        {formatEmployeeLabel(employee)}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label>{t('tasks.priority', 'Priority')}</Label>
                            <select
                                className="w-full border rounded-md px-3 py-2 text-sm bg-white"
                                value={priority}
                                onChange={(e) => setPriority(e.target.value as Task["priority"])}
                            >
                                <option value="low">{t('priority.low', 'Low')}</option>
                                <option value="medium">{t('priority.medium', 'Medium')}</option>
                                <option value="high">{t('priority.high', 'High')}</option>
                                <option value="urgent">{t('priority.urgent', 'Urgent')}</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label>{t('common.status', 'Status')}</Label>
                            <select
                                className="w-full border rounded-md px-3 py-2 text-sm bg-white"
                                value={status}
                                onChange={(e) => setStatus(e.target.value as Task["status"])}
                            >
                                <option value="pending">{t('status.pending', 'Pending')}</option>
                                <option value="in_progress">{t('status.in_progress', 'In Progress')}</option>
                                <option value="completed">{t('status.completed', 'Completed')}</option>
                                <option value="cancelled">{t('status.cancelled', 'Cancelled')}</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label>{t('tasks.due_date', 'Due Date')}</Label>
                            <Input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Label>{t('common.description', 'Description')}</Label>
                        <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
                    </div>
                    <div>
                        <Button onClick={handleCreateTask} disabled={creating}>
                            <Plus className="mr-2 h-4 w-4" />
                            {creating ? t('tasks.creating', 'Creating...') : t('tasks.create_button', 'Create Task')}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>{t('tasks.task_list', 'Task List')}</CardTitle>
                    <CardDescription>{t('tasks.latest_tasks', 'Latest tasks in your company.')}</CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="text-sm text-muted-foreground">{t('common.loading', 'Loading tasks...')}</div>
                    ) : tasks.length === 0 ? (
                        <div className="text-sm text-muted-foreground">{t('tasks.no_tasks', 'No tasks yet.')}</div>
                    ) : (
                        <div className="space-y-3">
                            {tasks.map((task) => (
                                <div key={task.id} className="border rounded-lg p-3 bg-white">
                                    <div className="flex items-center justify-between">
                                        <div className="font-semibold text-sm">{task.title}</div>
                                        <div className="flex gap-2">
                                            <Badge variant="outline">{task.priority}</Badge>
                                            <select
                                                className="border rounded-md px-2 py-1 text-xs bg-white"
                                                value={task.status}
                                                onChange={async (e) => {
                                                    const nextStatus = e.target.value as Task["status"];
                                                    await tasksApi.updateTask(task.id, { status: nextStatus });
                                                    setTasks((prev) =>
                                                        prev.map((t) =>
                                                            t.id === task.id ? { ...t, status: nextStatus } : t
                                                        )
                                                    );
                                                }}
                                            >
                                                <option value="pending">{t('status.pending', 'Pending')}</option>
                                                <option value="in_progress">{t('status.in_progress', 'In Progress')}</option>
                                                <option value="completed">{t('status.completed', 'Completed')}</option>
                                                <option value="cancelled">{t('status.cancelled', 'Cancelled')}</option>
                                            </select>
                                        </div>
                                    </div>
                                    {task.description && (
                                        <div className="text-xs text-muted-foreground mt-1">
                                            {task.description}
                                        </div>
                                    )}
                                    <div className="mt-2 flex flex-col gap-2 text-[10px] text-muted-foreground">
                                        <div>{t('tasks.due', 'Due')}: {task.due_date || t('tasks.na', 'N/A')}</div>
                                        <div className="flex items-center gap-2">
                                            <span>{t('tasks.assigned', 'Assigned')}:</span>
                                            <select
                                                className="border rounded-md px-2 py-1 text-[10px] bg-white"
                                                value={task.assigned_to || ""}
                                                onChange={async (e) => {
                                                    const nextAssigned = e.target.value || undefined;
                                                    await tasksApi.updateTask(task.id, { assigned_to: nextAssigned });
                                                    setTasks((prev) =>
                                                        prev.map((t) =>
                                                            t.id === task.id ? { ...t, assigned_to: nextAssigned } : t
                                                        )
                                                    );
                                                }}
                                                disabled={employeesLoading}
                                            >
                                                <option value="">{formatEmployeeLabel(undefined)}</option>
                                                {employees.map((employee) => (
                                                    <option key={employee.id} value={employee.id}>
                                                        {formatEmployeeLabel(employee)}
                                                    </option>
                                                ))}
                                            </select>
                                            <span className="text-[10px] text-muted-foreground">
                                                {task.assigned_to ? formatEmployeeLabel(employeeMap.get(task.assigned_to)) : ""}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
