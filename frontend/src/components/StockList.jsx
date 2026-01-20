import React, { useEffect, useState } from 'react';
import { getCompanies } from '../services/api';

const StockList = ({ onSelect }) => {
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCompanies = async () => {
            try {
                const data = await getCompanies();
                setCompanies(data.companies || []);
            } catch (error) {
                console.error("Failed to load companies");
            } finally {
                setLoading(false);
            }
        };

        fetchCompanies();
    }, []);

    if (loading) return <div className="p-4 text-gray-300">Loading companies...</div>;

    return (
        <div className="flex flex-col h-full bg-gray-900 border-r border-gray-800 w-64">
            <h2 className="text-xl font-bold p-4 text-white border-b border-gray-800">Companies</h2>
            <ul className="flex-1 overflow-y-auto">
                {companies.map((company) => (
                    <li key={company.ticker}>
                        <button
                            onClick={() => onSelect(company.ticker)}
                            className="w-full text-left px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors border-b border-gray-800 border-opacity-30 group"
                        >
                            <div className="font-medium text-white">{company.name || company.ticker}</div>
                            <div className="text-xs text-gray-500 group-hover:text-gray-400">{company.ticker}</div>
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default StockList;
