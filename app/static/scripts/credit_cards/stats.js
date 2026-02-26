import { getData, CURRENT_YEAR, MONTHS } from '../utils/generateChart.js';

const creditCardId = document.getElementById('credit-card-id').value;
const yearlyExpenseCanvas = document.getElementById('yearly-stats');

const yearlySingleModelReportEndpoint = document.getElementById('yearly-single-model-report-endpoint').value;
const yearlyTotalPerAssociationInfo = document.getElementById('get-yearly-total-per-association-info').value;

const chartTitle = document.getElementById('chart-title');
const yearSelect = document.getElementById('year-select');
const chartTitleTextContent = document.getElementById('chart-title').textContent;

let yearlyChartInstance = null;

function generateYearlyChart(canvas, type, expensesData, creditCardPaymentsData, loansData) {
if (yearlyChartInstance) {
        yearlyChartInstance.destroy();
    }

    yearlyChartInstance = new Chart(canvas, {
        type: type,
        data: {
            labels: MONTHS,
            datasets: [
                {
                    label: 'Expenses',
                    data: expensesData,
                    backgroundColor: "rgb(243, 0, 53)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    borderWidth: 1
                },
                {
                    label: 'Credit Card Payments',
                    data: creditCardPaymentsData,
                    backgroundColor: "#48b626",
                    borderColor: "#00f784",
                    borderWidth: 1
                },
                {
                    label: 'Loans',
                    data: loansData,
                    backgroundColor: "#ffc106",
                    borderColor: "#ffc106",
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

async function showChart(year, endpoint){
    const data = await getData(
        endpoint, 
        {
            credit_card_id: creditCardId,
            year: year
        }
    );

    generateYearlyChart(
        yearlyExpenseCanvas, 
        'line', 
        data.associations_info.expenses, 
        data.associations_info.credit_card_payments,
        data.associations_info.loans
    );
}

document.addEventListener('DOMContentLoaded',async (event) => {
    await showChart(CURRENT_YEAR, yearlyTotalPerAssociationInfo)
    chartTitle.textContent = chartTitleTextContent + ' - ' + CURRENT_YEAR;
});

yearSelect.addEventListener('change', async (event) => {
    const selectedYear = event.target.value;
    await showChart(selectedYear, yearlyTotalPerAssociationInfo)
    chartTitle.textContent = chartTitleTextContent + ' - ' + selectedYear;
});