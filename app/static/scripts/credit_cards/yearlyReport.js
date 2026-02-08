import { getData, CURRENT_YEAR } from '../utils/generateChart.js';

const creditCardYearlyReportEndpoint = document.getElementById('credit-card-yearly-report-endpoint').value;
const creditCardYearlyReportYearSpan = document.getElementById('credit-card-yearly-report-year-span');
const yearlyTotalPerAssociationCanvas = document.getElementById('yearly-stats');
const yearSelect = document.getElementById('year-select');

let yearlyLineChartInstance = null; 

function generateYearlyTotalPerAssociationChart(canvas, type, data){
    try {
        if (yearlyLineChartInstance) {
            yearlyLineChartInstance.destroy();
        }

        yearlyLineChartInstance = new Chart(canvas, {
                type: type,
                data: {
                    labels: data.months,
                    datasets: [
                        {
                            label: 'Expenses',
                            data: data.report.expenses,
                            backgroundColor: "#dd3445",
                            borderColor: "#dd3445",
                            borderWidth: 1                       
                        },
                        {
                            label: 'Credit Card Payments',
                            data: data.report.credit_card_payments,
                            backgroundColor: "#48b626",
                            borderColor: "#48b626",
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
    } catch (error) {
        console.error(error);
        throw new Error();
    }
}

document.addEventListener('DOMContentLoaded', async e => {
    let payload = {
        "year": CURRENT_YEAR
    }

    let data = await getData(creditCardYearlyReportEndpoint, payload);
    await generateYearlyTotalPerAssociationChart(yearlyTotalPerAssociationCanvas, 'line', data);

    creditCardYearlyReportYearSpan.textContent = CURRENT_YEAR.toString();
});

yearSelect.addEventListener('change', async e => {
    const selectedYear = e.target.value;
    let payload = {
        "year": selectedYear
    }

    let data = await getData(creditCardYearlyReportEndpoint, payload);
    await generateYearlyTotalPerAssociationChart(yearlyTotalPerAssociationCanvas, 'line', data);

    creditCardYearlyReportYearSpan.textContent = selectedYear.toString();
});