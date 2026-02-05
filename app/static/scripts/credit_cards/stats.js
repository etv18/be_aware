import { getData, CURRENT_YEAR, MONTHS } from '../utils/generateChart.js';

const yearlyExpenseCanvas = document.getElementById('yearly-stats');
const yearlySingleModelReportEndpoint = document.getElementById('yearly-single-model-report-endpoint').value;
const chartTitle = document.getElementById('chart-title');
const yearSelect = document.getElementById('year-select');
const chartTitleTextContent = document.getElementById('chart-title').textContent;

let yearlyChartInstance = null;

function generateYearlyChart(canvas, type, expensesData, creditCardPaymentsData){
if (yearlyChartInstance) {
        yearlyChartInstance.destroy();
    }

    yearlyChartInstance = new Chart(canvas, {
        type: type,
        data: {
            labels: MONTHS,
            datasets: [
                {
                    label: expensesData.label,
                    data: expensesData.expenses,
                    backgroundColor: "rgb(243, 0, 53)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    borderWidth: 1
                },
                {
                    label: creditCardPaymentsData.label,
                    data: creditCardPaymentsData.credit_card_payments,
                    backgroundColor: "#48b626",
                    borderColor: "#00f784",
                    borderWidth: 1
                }                                          
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

async function showChart(year, endpoint){
        const creditCardPaymentsData = await getData(
        endpoint, 
        {
            model: 'credit_card_payments',
            year: year
        }
    );
    const expensesData = await getData(
        endpoint, 
        {
            model: 'expenses',
            year: year
        }
    );

    generateYearlyChart(yearlyExpenseCanvas, 'line', expensesData, creditCardPaymentsData);
}

document.addEventListener('DOMContentLoaded',async (event) => {
    await showChart(CURRENT_YEAR, yearlySingleModelReportEndpoint)
    chartTitle.textContent = chartTitleTextContent + ' - ' + CURRENT_YEAR;
});

yearSelect.addEventListener('change', async (event) => {
    const selectedYear = event.target.value;
    await showChart(selectedYear, yearlySingleModelReportEndpoint)
    chartTitle.textContent = chartTitleTextContent + ' - ' + selectedYear;
});