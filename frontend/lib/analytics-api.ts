import { api } from "./api";
import { AnalyticsDashboardResponse, AnalyticsFilter } from "./types/analytics";

export const analyticsApi = {
    getDashboardMetrics: async (filter: AnalyticsFilter): Promise<AnalyticsDashboardResponse> => {
        const response = await api.post("/analytics/dashboard", filter);
        return response.data;
    },

    exportReport: async (filter: AnalyticsFilter, format: "csv" | "pdf", reportType: string) => {
        const response = await api.post(
            `/analytics/export`,
            filter,
            {
                params: { format, report_type: reportType },
                responseType: 'blob'
            }
        );
        // Create a blob from the response
        const blob = new Blob([response.data], { type: format === 'pdf' ? 'application/pdf' : 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // Attempt to extract filename from content-disposition
        const contentDisposition = response.headers['content-disposition'];
        let filename = `report_${new Date().toISOString()}.csv`;
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (fileNameMatch && fileNameMatch.length === 2)
                filename = fileNameMatch[1];
        }

        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
    },
};
