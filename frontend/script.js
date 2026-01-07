const API_BASE = "http://127.0.0.1:8000";

let chartInstance = null;
let currentSymbol = null;
const TIMEFRAME_LABELS = {
    "30d": "Last 30 Days",
    "90d": "Last 90 Days",
    "6mo": "Last 6 Months",
    "1y": "Last 1 Year",
};

// DOM Elements
const companiesContainer = document.getElementById("companiesContainer");
const selectedCompanyName = document.getElementById("selectedCompanyName");
const selectedCompanySymbol = document.getElementById("selectedCompanySymbol");
const statsGrid = document.getElementById("statsGrid");
const chartCard = document.getElementById("chartCard");
const placeholder = document.getElementById("placeholder");
const comparisonView = document.getElementById("comparisonView");
const compareBtn = document.getElementById("compareBtn");
const runComparison = document.getElementById("runComparison");
const compSelect1 = document.getElementById("compSelect1");
const compSelect2 = document.getElementById("compSelect2");
const comparisonResults = document.getElementById("comparisonResults");

// Load companies on page load
window.onload = async () => {
    try {
        const res = await fetch(`${API_BASE}/companies`);
        const companies = await res.json();
        renderCompanyList(companies);
        populateComparisonSelects(companies);
    } catch (error) {
        console.error("Error loading companies:", error);
        companiesContainer.innerHTML = `<p class="text-red-500 text-sm">Failed to load companies. Is the backend running?</p>`;
    }
};

function getSelectedTimeframe() {
    return document.getElementById("timeframeSelect").value;
}

function updateChartTitle(timeframe) {
    const label = TIMEFRAME_LABELS[timeframe] || "Custom Range";
    document.getElementById("chartTitle").textContent =
        `Price History (${label})`;
}

function renderCompanyList(companies) {
    companiesContainer.innerHTML = "";
    companies.forEach(company => {
        const div = document.createElement("div");
        div.className = "sidebar-item p-3 rounded-lg cursor-pointer transition duration-150 flex items-center";
        div.innerHTML = `
            <div class="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center mr-3 font-bold text-xs">
                ${company.symbol.split('.')[0][0]}
            </div>
            <div>
                <p class="text-sm font-semibold">${company.name}</p>
                <p class="text-xs text-gray-500">${company.symbol}</p>
            </div>
        `;
        div.onclick = () => selectCompany(company);
        div.setAttribute("data-symbol", company.symbol);
        companiesContainer.appendChild(div);
    });
}

function populateComparisonSelects(companies) {
    [compSelect1, compSelect2].forEach(select => {
        select.innerHTML = companies.map(c => `<option value="${c.symbol}">${c.name} (${c.symbol})</option>`).join("");
    });
}

async function selectCompany(company) {
    // UI Updates
    document.querySelectorAll(".sidebar-item").forEach(el => el.classList.remove("active"));
    document.querySelector(`[data-symbol="${company.symbol}"]`).classList.add("active");
    
    currentSymbol = company.symbol;
    selectedCompanyName.textContent = company.name;
    selectedCompanySymbol.textContent = company.symbol;
    
    placeholder.classList.add("hidden");
    comparisonView.classList.add("hidden");
    statsGrid.classList.remove("hidden");
    chartCard.classList.remove("hidden");

    const timeframe = getSelectedTimeframe();
    updateChartTitle(timeframe);
    // Fetch Data
    await Promise.all([
        loadSummary(company.symbol, timeframe),
        loadChartData(company.symbol, timeframe)
    ]);
}

async function loadSummary(symbol, timeframe) {
    try {
        const res = await fetch(`${API_BASE}/summary/${symbol}?timeframe=${timeframe}`);
        const data = await res.json();
        
        document.getElementById("statClose").textContent = `₹${data.latest_close.toLocaleString()}`;
        
        const trendEl = document.getElementById("statTrend");
        trendEl.textContent = data.short_term_trend;
        trendEl.className = `text-2xl font-bold capitalize ${data.short_term_trend === 'up' ? 'text-green-500' : 'text-red-500'}`;
        
        document.getElementById("statVolatility").textContent = `${data.volatility.value_percent}% (${data.volatility.label})`;
        
        const pos52w = data.position_in_52_week_range_percent;
        document.getElementById("stat52wBar").style.width = `${pos52w}%`;
        document.getElementById("stat52wLabel").textContent = `${pos52w}% of 52W Range`;
    } catch (error) {
        console.error("Error loading summary:", error);
    }
}

async function loadChartData(symbol, timeframe) {
    try {
        const res = await fetch(`${API_BASE}/data`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol, timeframe })
        });
        const data = await res.json();
        drawChart(data);
    } catch (error) {
        console.error("Error loading chart data:", error);
    }
}

function drawChart(data) {
    const ctx = document.getElementById("priceChart").getContext("2d");
    
    if (chartInstance) {
        chartInstance.destroy();
    }

    const labels = data.map(d => new Date(d.Date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }));
    const prices = data.map(d => d.Close);

    chartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Close Price",
                data: prices,
                borderColor: "#3b82f6",
                backgroundColor: "rgba(59, 130, 246, 0.1)",
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1f2937',
                    padding: 12,
                    titleFont: { size: 14 },
                    bodyFont: { size: 14 },
                    callbacks: {
                        label: function(context) {
                            return ` ₹${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    grid: { color: "#f3f4f6" },
                    ticks: {
                        callback: value => "₹" + value.toLocaleString()
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

// Comparison Logic
compareBtn.onclick = () => {
    placeholder.classList.add("hidden");
    statsGrid.classList.add("hidden");
    chartCard.classList.add("hidden");
    comparisonView.classList.remove("hidden");
    
    selectedCompanyName.textContent = "Compare Stocks";
    selectedCompanySymbol.textContent = "Evaluate performance between two companies";
    
    document.querySelectorAll(".sidebar-item").forEach(el => el.classList.remove("active"));
};

runComparison.onclick = async () => {
    const s1 = compSelect1.value;
    const s2 = compSelect2.value;
    
    try {
        const res = await fetch(`${API_BASE}/compare/${s1}/${s2}`);
        const data = await res.json();
        renderComparison(data);
    } catch (error) {
        console.error("Comparison error:", error);
    }
};

document.getElementById("timeframeSelect").addEventListener("change", () => {
    if (!currentSymbol) return;

    const timeframe = getSelectedTimeframe();
    updateChartTitle(timeframe);
    loadSummary(currentSymbol, timeframe);
    loadChartData(currentSymbol, timeframe);
});


function renderComparison(data) {
    comparisonResults.classList.remove("hidden");
    comparisonResults.innerHTML = `
        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                <i class="fas fa-info-circle mr-2 text-blue-500"></i> Comparison Insights
            </h4>
            <div class="space-y-4">
                <div class="p-3 bg-gray-50 rounded-lg">
                    <p class="text-sm text-gray-500">More Volatile</p>
                    <p class="font-bold text-lg">${data.comparison.more_volatile || 'Equal'}</p>
                </div>
                <div class="p-3 bg-gray-50 rounded-lg">
                    <p class="text-sm text-gray-500">Closer to 52W High</p>
                    <p class="font-bold text-lg">${data.comparison.closer_to_52_week_high || 'Equal'}</p>
                </div>
            </div>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                <i class="fas fa-bullseye mr-2 text-blue-500"></i> Current Trends
            </h4>
            <div class="space-y-4">
                <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span class="font-semibold">${data.stock_1.symbol}</span>
                    <span class="px-3 py-1 rounded-full text-xs font-bold uppercase ${data.stock_1.short_term_trend === 'up' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                        ${data.stock_1.short_term_trend}
                    </span>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span class="font-semibold">${data.stock_2.symbol}</span>
                    <span class="px-3 py-1 rounded-full text-xs font-bold uppercase ${data.stock_2.short_term_trend === 'up' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                        ${data.stock_2.short_term_trend}
                    </span>
                </div>
            </div>
        </div>
    `;
}
