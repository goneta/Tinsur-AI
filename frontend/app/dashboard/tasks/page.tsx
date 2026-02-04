"use client";

import { useEffect, useMemo, useState } from "react";
import { tasksApi, Task } from "@/lib/tasks-api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { ClipboardList, Plus } from "lucide-react";

export default function TasksPage() {
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
                title: "Error",
                description: "Failed to load tasks.",
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
                    title: "Error",
                    description: "Failed to load employees.",
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
        if (!employee) return "Unassigned";
        const fullName = [employee.first_name, employee.last_name].filter(Boolean).join(" ").trim();
        return fullName || employee.email || "Unassigned";
    };

    const handleCreateTask = async () => {
        if (!title.trim()) {
            toast({
                title: "Missing title",
                description: "Please provide a task title.",
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
                title: "Task created",
                description: "The task has been added successfully.",
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to create task.",
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
                    <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
                    <p className="text-muted-foreground mt-2">
                        Track internal work items, follow-ups, and approvals.
                    </p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <ClipboardList className="h-4 w-4" /> Create Task
                    </CardTitle>
                    <CardDescription>Add a new task for your team.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>Title</Label>
                            <Input value={title} onChange={(e) => setTitle(e.target.value)} />
                        </div>
                        <div className="space-y-2">
                            <Label>Assigned To</Label>
                            <select
                                className="w-full border rounded-md px-3 py-2 text-sm bg-white"
                                value={assignedTo}
                                onChange={(e) => setAssignedTo(e.target.value)}
                                disabled={employeesLoading}
                            >
                                <option value="">Unassigned</option>
                                {employees.map((employee) => (
                                    <option key={employee.id} value={employee.id}>
                                        {formatEmployeeLabel(employee)}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label>Priority</Label>
                            <select
                                className="w-full border rounded-md px-3 py-2 text-sm bg-white"
                                value={priority}
                                onChange={(e) => setPriority(e.target.value as Task["priority"])}
                            >
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="urgent">Urgent</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label>Status</Label>
                            <select
                                className="w-full border rounded-md px-3 py-2 text-sm bg-white"
                                value={status}
                                onChange={(e) => setStatus(e.target.value as Task["status"])}
                            >
                                <option value="pending">Pending</option>
                                <option value="in_progress">In Progress</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label>Due Date</Label>
                            <Input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Label>Description</Label>
                        <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
                    </div>
                    <div>
                        <Button onClick={handleCreateTask} disabled={creating}>
                            <Plus className="mr-2 h-4 w-4" />
                            {creating ? "Creating..." : "Create Task"}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Task List</CardTitle>
                    <CardDescription>Latest tasks in your company.</CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="text-sm text-muted-foreground">Loading tasks...</div>
                    ) : tasks.length === 0 ? (
                        <div className="text-sm text-muted-foreground">No tasks yet.</div>
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
                                                <option value="pending">Pending</option>
                                                <option value="in_progress">In Progress</option>
                                                <option value="completed">Completed</option>
                                                <option value="cancelled">Cancelled</option>
                                            </select>
                                        </div>
                                    </div>
                                    {task.description && (
                                        <div className="text-xs text-muted-foreground mt-1">
                                            {task.description}
                                        </div>
                                    )}
                                    <div className="mt-2 flex flex-col gap-2 text-[10px] text-muted-foreground">
                                        <div>Due: {task.due_date || "N/A"}</div>
                                        <div className="flex items-center gap-2">
                                            <span>Assigned:</span>
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
