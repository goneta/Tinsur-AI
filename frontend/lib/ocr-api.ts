import { api } from "./api";

export interface OCRResult {
    document_id: string;
    document_type: string;
    extraction_method: string;
    extracted_fields: Record<string, any>;
    confidence_scores: Record<string, any>;
    validation_status: string;
    created_at: string;
}

export const ocrApi = {
    processDocument: async (file: File, documentType?: string) => {
        const formData = new FormData();
        formData.append("document", file);

        const query = documentType ? `?document_type=${encodeURIComponent(documentType)}` : "";
        const response = await api.post<OCRResult>(`/ocr/process${query}`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        return response.data;
    },

    getResult: async (documentId: string) => {
        const response = await api.get<OCRResult>(`/ocr/results/${documentId}`);
        return response.data;
    },

    verifyResult: async (documentId: string, status: "verified" | "rejected", notes?: string) => {
        const response = await api.post<OCRResult>("/ocr/verify", {
            document_id: documentId,
            status,
            notes,
        });
        return response.data;
    },
};
