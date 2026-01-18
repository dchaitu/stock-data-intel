import React, { useState } from 'react';
import StockList from './components/StockList';
import StockChart from './components/StockChart';

function App() {
    const [selectedTicker, setSelectedTicker] = useState(null);

    return (
        <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
            <StockList onSelect={setSelectedTicker} />
            <main className="flex-1 overflow-y-auto">
                <header className="bg-gray-900 border-b border-gray-800 p-4 shadow-sm">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
                        Stock Data Intel
                    </h1>
                </header>
                <div className="h-[calc(100vh-64px)]">
                    <StockChart ticker={selectedTicker} />
                </div>
            </main>
        </div>
    );
}

export default App;
