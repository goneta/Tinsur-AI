import { QuoteDetails } from "@/components/quotes/quote-details";

interface PageProps {
    params: Promise<{
        id: string;
    }>;
}

export default async function QuoteIdPage({ params }: PageProps) {
    const { id } = await params;
    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <QuoteDetails id={id} />
        </div>
    );
}
