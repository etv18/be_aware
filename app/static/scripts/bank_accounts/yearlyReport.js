import { getData, CURRENT_YEAR } from '../utils/generateChart.js';

const bankAccountYearlyReportEndpoint = document.getElementById('bank-account-yearly-report-endpoint').value;
const bankAccountYearlyReportYearSpan = document.getElementById('bank-account-yearly-report-year-span');
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
                            label: 'Withdrawals',
                            data: data.report.withdrawals,
                            backgroundColor: "#b9dc88",
                            borderColor: "#b9dc88",
                            borderWidth: 1 
                        },
                        {
                            label: 'Loans',
                            data: data.report.loans,
                            backgroundColor: "#ffc106",
                            borderColor: "#ffc106",
                            borderWidth: 1 
                        },
                        {
                            label: 'Credit Card Payments',
                            data: data.report.credit_card_payments,
                            backgroundColor: "#6d747c",
                            borderColor: "#6d747c",
                            borderWidth: 1 
                        },
                        {
                            label: 'Debt Payments',
                            data: data.report.debt_payments,
                            backgroundColor: "#3a768b",
                            borderColor: "#3a768b",
                            borderWidth: 1 
                        },
                        {
                            label: 'Loan Payment',
                            data: data.report.loan_payment,
                            backgroundColor: "#198754",
                            borderColor: "#198754",
                            borderWidth: 1 
                        },
                        {
                            label: 'Incomes',
                            data: data.report.incomes,
                            backgroundColor: "#0d6efd",
                            borderColor: "#0d6efd",
                            borderWidth: 1 
                        },
                        {
                            label: 'Deposits',
                            data: data.report.deposits,
                            backgroundColor: "#624ea2",
                            borderColor: "#624ea2",
                            borderWidth: 1 
                        },
                        {
                            label: 'Debts',
                            data: data.report.debts,
                            backgroundColor: "#dfbab1",
                            borderColor: "#dfbab1",
                            borderWidth: 1 
                        },
                        {
                            label: 'Bank Transfers',
                            data: data.report.bank_transfers,
                            backgroundColor: "#8a4331ea",
                            borderColor: "#8a4331ea",
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

    let data = await getData(bankAccountYearlyReportEndpoint, payload);
    await generateYearlyTotalPerAssociationChart(yearlyTotalPerAssociationCanvas, 'line', data);

    bankAccountYearlyReportYearSpan.textContent = CURRENT_YEAR.toString();
});

yearSelect.addEventListener('change', async e => {
    const selectedYear = e.target.value;
    let payload = {
        "year": selectedYear
    }

    let data = await getData(bankAccountYearlyReportEndpoint, payload);
    await generateYearlyTotalPerAssociationChart(yearlyTotalPerAssociationCanvas, 'line', data);

    bankAccountYearlyReportYearSpan.textContent = selectedYear.toString();
});