"use client";

import { useEffect, useMemo, useState } from "react";
import { chatApi, ChatChannel, ChatMessage } from "@/lib/chat-api";
import { tasksApi } from "@/lib/tasks-api";
import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { MessageSquare, Plus, Send } from "lucide-react";

export default function ChatPage() {
    const { toast } = useToast();
    const { user } = useAuth();
    const [channels, setChannels] = useState<ChatChannel[]>([]);
    const [selectedChannel, setSelectedChannel] = useState<ChatChannel | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(true);
    const [creatingChannel, setCreatingChannel] = useState(false);
    const [newChannelName, setNewChannelName] = useState("");
    const [newChannelPrivate, setNewChannelPrivate] = useState(false);
    const [invitees, setInvitees] = useState<string[]>([]);
    const [newMessage, setNewMessage] = useState("");
    const [employees, setEmployees] = useState<Array<{ id: string; first_name?: string; last_name?: string; email?: string }>>([]);
    const [members, setMembers] = useState<string[]>([]);
    const reactionOptions = ["👍", "✅", "🔥"];

    const loadChannels = async () => {
        try {
            const data = await chatApi.listChannels();
            setChannels(data);
            if (!selectedChannel && data.length > 0) {
                setSelectedChannel(data[0]);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load chat channels.",
                variant: "destructive",
            });
        }
    };

    const loadMessages = async (channelId: string) => {
        try {
            setLoading(true);
            const data = await chatApi.listMessages(channelId);
            setMessages(data);
            if (user?.id) {
                await Promise.all(
                    data
                        .filter((msg) => !(msg.read_by || []).includes(user.id))
                        .map((msg) => chatApi.markMessageRead(msg.id))
                );
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load messages.",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const loadEmployees = async () => {
        try {
            const data = await tasksApi.listEmployees();
            setEmployees(data || []);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load employees.",
                variant: "destructive",
            });
        }
    };

    const loadMembers = async (channelId: string) => {
        try {
            const data = await chatApi.listChannelMembers(channelId);
            setMembers(data.map((member) => member.user_id));
        } catch (error) {
            setMembers([]);
        }
    };

    useEffect(() => {
        loadChannels();
        loadEmployees();
    }, []);

    useEffect(() => {
        if (selectedChannel) {
            loadMessages(selectedChannel.id);
            if (selectedChannel.is_private) {
                loadMembers(selectedChannel.id);
            } else {
                setMembers([]);
            }
        }
    }, [selectedChannel?.id]);

    const handleCreateChannel = async () => {
        if (!newChannelName.trim()) return;
        try {
            setCreatingChannel(true);
            await chatApi.createChannel(
                newChannelName.trim(),
                newChannelPrivate,
                newChannelPrivate ? invitees : undefined
            );
            setNewChannelName("");
            setNewChannelPrivate(false);
            setInvitees([]);
            await loadChannels();
            toast({
                title: "Channel created",
                description: "New channel is ready.",
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to create channel.",
                variant: "destructive",
            });
        } finally {
            setCreatingChannel(false);
        }
    };

    const handleInviteMembers = async (channelId: string) => {
        if (invitees.length === 0) return;
        try {
            await chatApi.inviteChannelMembers(channelId, invitees);
            setInvitees([]);
            await loadMembers(channelId);
            toast({
                title: "Members added",
                description: "Invitations sent successfully.",
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to invite members.",
                variant: "destructive",
            });
        }
    };

    const handleSendMessage = async () => {
        if (!selectedChannel || !newMessage.trim()) return;
        try {
            await chatApi.sendMessage(selectedChannel.id, newMessage.trim());
            setNewMessage("");
            await loadMessages(selectedChannel.id);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to send message.",
                variant: "destructive",
            });
        }
    };

    const handleReact = async (message: ChatMessage, emoji: string) => {
        try {
            const hasReacted = !!message.reactions?.find(
                (r) => r.emoji === emoji && r.user_id === user?.id
            );
            await chatApi.reactToMessage(message.id, emoji, hasReacted ? "remove" : "add");
            if (selectedChannel) {
                await loadMessages(selectedChannel.id);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update reaction.",
                variant: "destructive",
            });
        }
    };

    const formatEmployeeLabel = (employee?: { first_name?: string; last_name?: string; email?: string }) => {
        if (!employee) return "Unknown";
        const fullName = [employee.first_name, employee.last_name].filter(Boolean).join(" ").trim();
        return fullName || employee.email || "Unknown";
    };

    const employeeMap = useMemo(() => {
        const map = new Map<string, { first_name?: string; last_name?: string; email?: string }>();
        employees.forEach((employee) => map.set(employee.id, employee));
        return map;
    }, [employees]);

    const availableInvitees = employees.filter(
        (employee) => !(selectedChannel?.is_private && members.includes(employee.id))
    );

    return (
        <div className="flex flex-col gap-6 p-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Internal Chat</h1>
                <p className="text-muted-foreground mt-2">
                    Collaborate with your team in real time.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-1">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <MessageSquare className="h-4 w-4" /> Channels
                        </CardTitle>
                        <CardDescription>Pick a channel or create a new one.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>New Channel</Label>
                            <div className="flex gap-2">
                                <Input
                                    value={newChannelName}
                                    onChange={(e) => setNewChannelName(e.target.value)}
                                    placeholder="e.g. Claims Team"
                                />
                                <Button onClick={handleCreateChannel} disabled={creatingChannel}>
                                    <Plus className="h-4 w-4" />
                                </Button>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <input
                                    type="checkbox"
                                    checked={newChannelPrivate}
                                    onChange={(e) => setNewChannelPrivate(e.target.checked)}
                                />
                                <span>Private channel</span>
                            </div>
                            {newChannelPrivate && (
                                <div className="flex flex-col gap-2">
                                    <Label className="text-xs">Invite members</Label>
                                    <select
                                        className="w-full border rounded-md px-2 py-2 text-xs bg-white"
                                        multiple
                                        value={invitees}
                                        onChange={(e) => {
                                            const selected = Array.from(e.target.selectedOptions).map((opt) => opt.value);
                                            setInvitees(selected);
                                        }}
                                    >
                                        {employees.map((employee) => (
                                            <option key={employee.id} value={employee.id}>
                                                {formatEmployeeLabel(employee)}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}
                        </div>

                        <div className="space-y-2">
                            {channels.length === 0 ? (
                                <div className="text-sm text-muted-foreground">No channels yet.</div>
                            ) : (
                                channels.map((channel) => (
                                    <button
                                        key={channel.id}
                                        onClick={() => setSelectedChannel(channel)}
                                        className={`w-full text-left px-3 py-2 rounded-md border ${
                                            selectedChannel?.id === channel.id
                                                ? "bg-slate-100 border-slate-300"
                                                : "bg-white"
                                        }`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <span>{channel.name}</span>
                                            {channel.is_private && (
                                                <span className="text-[10px] uppercase bg-slate-200 text-slate-700 px-2 py-0.5 rounded">
                                                    Private
                                                </span>
                                            )}
                                        </div>
                                    </button>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>

                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Messages</CardTitle>
                        <CardDescription>
                            {selectedChannel ? `Channel: ${selectedChannel.name}` : "Select a channel"}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {selectedChannel?.is_private && (
                            <div className="border rounded-md p-3 bg-white">
                                <div className="text-xs font-semibold text-slate-600 mb-2">
                                    Private members
                                </div>
                                <div className="flex flex-wrap gap-2 text-[10px] text-slate-500 mb-3">
                                    {members.length === 0 ? (
                                        <span>No members yet.</span>
                                    ) : (
                                        members.map((memberId) => (
                                            <span key={memberId} className="px-2 py-1 bg-slate-100 rounded">
                                                {formatEmployeeLabel(employeeMap.get(memberId))}
                                            </span>
                                        ))
                                    )}
                                </div>
                                <div className="flex items-center gap-2">
                                    <select
                                        className="flex-1 border rounded-md px-2 py-2 text-xs bg-white"
                                        multiple
                                        value={invitees}
                                        onChange={(e) => {
                                            const selected = Array.from(e.target.selectedOptions).map((opt) => opt.value);
                                            setInvitees(selected);
                                        }}
                                    >
                                        {availableInvitees.map((employee) => (
                                            <option key={employee.id} value={employee.id}>
                                                {formatEmployeeLabel(employee)}
                                            </option>
                                        ))}
                                    </select>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleInviteMembers(selectedChannel.id)}
                                        disabled={invitees.length === 0}
                                    >
                                        Invite
                                    </Button>
                                </div>
                            </div>
                        )}
                        <div className="h-[360px] overflow-y-auto border rounded-md p-3 bg-slate-50">
                            {loading ? (
                                <div className="text-sm text-muted-foreground">Loading messages...</div>
                            ) : messages.length === 0 ? (
                                <div className="text-sm text-muted-foreground">No messages yet.</div>
                            ) : (
                                messages
                                    .slice()
                                    .reverse()
                                    .map((msg) => (
                                        <div key={msg.id} className="mb-3">
                                            <div className="text-[11px] text-slate-500">
                                                {new Date(msg.created_at).toLocaleString()}
                                            </div>
                                            <div className="text-sm bg-white border rounded-md p-2">
                                                {msg.message}
                                            </div>
                                            <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-500">
                                                <span>Reads: {(msg.read_by || []).length}</span>
                                                <div className="flex items-center gap-1">
                                                    {reactionOptions.map((emoji) => (
                                                        <button
                                                            key={emoji}
                                                            className={`px-1 rounded ${
                                                                msg.reactions?.some(
                                                                    (r) => r.emoji === emoji && r.user_id === user?.id
                                                                )
                                                                    ? "bg-slate-200"
                                                                    : "bg-transparent"
                                                            }`}
                                                            onClick={() => handleReact(msg, emoji)}
                                                        >
                                                            {emoji}{" "}
                                                            {
                                                                msg.reactions?.filter((r) => r.emoji === emoji).length ||
                                                                0
                                                            }
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    ))
                            )}
                        </div>
                        <div className="flex gap-2">
                            <Input
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                                placeholder="Write a message..."
                            />
                            <Button onClick={handleSendMessage} disabled={!selectedChannel}>
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
