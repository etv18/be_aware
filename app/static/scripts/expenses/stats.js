import { getData, generateYearlyAllModelsChart, CURRENT_YEAR } from '../utils/generateChart.js';

const yearlyExpenseCanvas = document.getElementById('yearly-stats');
const yearlySingleModelReportEndpoint = document.getElementById('yearly-single-model-report-endpoint').value;
const chartTitle = document.getElementById('chart-title');
const yearSelect = document.getElementById('year-select');
const chartTitleTextContent = document.getElementById('chart-title').textContent;

const BACKGROUND_COLOR = '#dd3445';
const BORDER_COLOR = '#dd3445';
const CHART_TYPE = 'line';
const MODEL = 'expenses';

document.addEventListener('DOMContentLoaded',async (event) => {
    const yearlyStatsData = await getData(
        yearlySingleModelReportEndpoint, 
        {
            model: MODEL,
            year: CURRENT_YEAR
        }
    );
    generateYearlyAllModelsChart(yearlyExpenseCanvas, CHART_TYPE, yearlyStatsData.label, yearlyStatsData[MODEL], BACKGROUND_COLOR, BORDER_COLOR);
    chartTitle.textContent = chartTitleTextContent + ' - ' + CURRENT_YEAR;
});

yearSelect.addEventListener('change', async (event) => {
    const selectedYear = event.target.value;
    const yearlyStatsData = await getData(
        yearlySingleModelReportEndpoint,
        {
            model: MODEL,
            year: selectedYear
        }
    );
    generateYearlyAllModelsChart(yearlyExpenseCanvas, CHART_TYPE, yearlyStatsData.label, yearlyStatsData[MODEL], BACKGROUND_COLOR, BORDER_COLOR);
    chartTitle.textContent = chartTitleTextContent + ' - ' + selectedYear;
});


/*
let yearlyStatsExpenseChartInstance = null;

async function getData(url, payload) {
    let data;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.log(errorData);
            return;
        }

        data = await response.json();
        console.log(data);
        
        return data;
    } catch (error) {
        console.error(error);
    }

}

function generateYearlyAllModelsChart(canvas, type, data){
if (yearlyStatsExpenseChartInstance) {
        yearlyStatsExpenseChartInstance.destroy();
    }

    yearlyStatsExpenseChartInstance = new Chart(canvas, {
        type: type,
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'Expenses',
                    data: data.expenses,
                    backgroundColor: "#dd3445",
                    borderColor: "#dd3445",
                    borderWidth: 1                       
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {stepSize: 500}
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded',async (event) => {
    const yearlyStatsData = await getData(
        yearlySingleModelReportEndpoint, 
        {
            model: 'expenses',
            year: 2026
        }
    );
    generateYearlyAllModelsChart(yearlyExpenseChart, 'line', yearlyStatsData);
});
*/