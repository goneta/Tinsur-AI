'use client';

import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup
} from "@/components/ui/resizable";
import { LeftPanel } from "./left-panel";
import { RightPanel } from "./right-panel";
import { useState } from "react";
import { PreviewState } from "@/types/ai-agent";
import { cn } from "@/lib/utils";
import { useChat } from "@/context/chat-context";

interface AgentWorkspaceProps {
    isGlobal?: boolean;
}

export function AgentWorkspace({ isGlobal }: AgentWorkspaceProps) {
    const { previewState, setPreviewState, pendingAction, setPendingAction } = useChat();

    return (
        <div className={cn(
            "h-full w-full overflow-hidden bg-background text-foreground",
            !isGlobal && "h-[calc(100vh-4rem)] border shadow-sm"
        )}>
            <ResizablePanelGroup direction="horizontal">
                <ResizablePanel defaultSize={40} minSize={30}>
                    <LeftPanel
                        onPreviewChange={setPreviewState}
                        pendingAction={pendingAction}
                        onActionProcessed={() => setPendingAction(null)}
                    />
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={60} minSize={30}>
                    <RightPanel
                        previewState={previewState}
                        onAction={(action, data) => setPendingAction({ action, data })}
                    />
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    );
}
