
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface ClientProfilePictureProps {
    src?: string
    fallback?: string
    className?: string
}

export function ClientProfilePicture({ src, fallback, className }: ClientProfilePictureProps) {
    return (
        <Avatar className={cn("h-8 w-8", className)}>
            <AvatarImage src={src} />
            <AvatarFallback>{fallback || "CL"}</AvatarFallback>
        </Avatar>
    )
}
