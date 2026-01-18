import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { getStockData, getStockSummary } from '../services/api';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const StockChart = ({ ticker }) => {
    const [chartData, setChartData] = useState(null);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!ticker) return;

        const fetchData = async () => {
            setLoading(true);
            try {
                const [histData, summaryData] = await Promise.all([
                    getStockData(ticker),
                    getStockSummary(ticker)
                ]);

                setSummary(summaryData);

                const labels = histData.map(d => new Date(d.date).toLocaleDateString());
                const prices = histData.map(d => d.close);
                const ma7 = histData.map(d => d.ma_7);

                setChartData({
                    labels,
                    datasets: [
                        {
                            label: 'Close Price',
                            data: prices,
                            borderColor: 'rgb(59, 130, 246)',
                            backgroundColor: 'rgba(59, 130, 246, 0.5)',
                            tension: 0.1
                        },
                        {
                            label: '7-Day MA',
                            data: ma7,
                            borderColor: 'rgb(249, 115, 22)',
                            backgroundColor: 'rgba(249, 115, 22, 0.5)',
                            borderDash: [5, 5],
                            tension: 0.1
                        }
                    ],
                });
            } catch (error) {
                console.error("Error loading chart data");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [ticker]);

    if (!ticker) return <div className="flex items-center justify-center h-full text-gray-500">Select a company to view data</div>;
    if (loading) return <div className="flex items-center justify-center h-full text-gray-300">Loading data...</div>;

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: { color: 'white' }
            },
            title: {
                display: true,
                text: `${ticker} Stock Price (Last 30 Days)`,
                color: 'white',
                font: { size: 16 }
            },
        },
        scales: {
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                ticks: { color: 'gray' }
            },
            x: {
                grid: { display: false },
                ticks: { color: 'gray' }
            }
        }
    };

    return (
        <div className="flex flex-col space-y-6 h-full p-6">
            {summary && (
                <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
                        <p className="text-gray-400 text-sm">52-Week High</p>
                        <p className="text-xl font-bold text-green-400">{summary.high_52w.toFixed(2)}</p>
                    </div>
                    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
                        <p className="text-gray-400 text-sm">52-Week Low</p>
                        <p className="text-xl font-bold text-red-400">{summary.low_52w.toFixed(2)}</p>
                    </div>
                    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
                        <p className="text-gray-400 text-sm">Avg Close (52W)</p>
                        <p className="text-xl font-bold text-blue-400">{summary.avg_close_52w.toFixed(2)}</p>
                    </div>
                </div>
            )}
            <div className="bg-gray-800 p-4 rounded-lg shadow-lg flex-1">
                {chartData && <Line options={options} data={chartData} />}
            </div>
        </div>
    );
};

export default StockChart;
