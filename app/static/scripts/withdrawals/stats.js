import { getData, generateYearlyAllModelsChart, CURRENT_YEAR } from '../utils/generateChart.js';

const yearlyExpenseCanvas = document.getElementById('yearly-stats');
const yearlySingleModelReportEndpoint = document.getElementById('yearly-single-model-report-endpoint').value;
const chartTitle = document.getElementById('chart-title');
const yearSelect = document.getElementById('year-select');
const chartTitleTextContent = document.getElementById('chart-title').textContent;

const BACKGROUND_COLOR = '#b9dc88';
const BORDER_COLOR = '#b9dc88';
const CHART_TYPE = 'line';
const MODEL = 'withdrawals';

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
