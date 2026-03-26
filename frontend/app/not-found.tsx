import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NotFound() {
    return (
        <div className="h-screen w-full flex flex-col items-center justify-center bg-background text-foreground space-y-4">
            <h1 className="text-4xl font-bold">404</h1>
            <h2 className="text-xl">Page Not Found</h2>
            <p className="text-muted-foreground">The page you are looking for does not exist.</p>
            <Link href="/dashboard">
                <Button variant="default">Return to Dashboard</Button>
            </Link>
        </div>
    );
}
