const API_BASE_URL = "http://localhost:8000/api/v1";

export const getCompanies = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/stocks/companies`);
        if (!response.ok) throw new Error("Failed to fetch companies");
        return await response.json();
    } catch (error) {
        console.error("Error fetching companies:", error);
        throw error;
    }
};

export const getStockData = async (ticker) => {
    try {
        const response = await fetch(`${API_BASE_URL}/stocks/data/${ticker}`);
        if (!response.ok) throw new Error("Failed to fetch stock data");
        return await response.json();
    } catch (error) {
        console.error(`Error fetching data for ${ticker}:`, error);
        throw error;
    }
};

export const getStockSummary = async (ticker) => {
    try {
        const response = await fetch(`${API_BASE_URL}/stocks/summary/${ticker}`);
        if (!response.ok) throw new Error("Failed to fetch summary");
        return await response.json();
    } catch (error) {
        console.error(`Error fetching summary for ${ticker}:`, error);
        throw error;
    }
};
