const monthlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-monthly');
const yearlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-yearly');
const yearlyStatsAllModelsChart = document.getElementById('yearly-stats-all-models');

const yearlyStatsAllModelsEndpoint = document.getElementById('yearly-stats-all-models-endpoint').value;

async function getMonthlyIncomeAndExpenseData(){
    try {
        const response = await fetch('/populate/monthly/expense_and_income_chart');
        if(!response.ok) {
            console.log(response.json());
            return;
        }
        const data = await response.json();

        return data;
    } catch (error) {
        console.error(error);
    }
    return null;
}

async function getYearlyIncomeAndExpenseData(){
    try {
        response = await fetch('/populate/yearly/expense_and_income_chart');
        if(!response.ok) {
            console.log(response.json());
            return;
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}


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

async function generateMontlyChart(canvas, type, data) {
    try {
        new Chart(canvas, {
            type: type,
            data: {
                labels: ['Incomes', 'Expenses'],
                datasets: [{
                    label: 'Amount',
                    data: [data.incomes, data.expenses],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {beginAtZero: true}
                }
            }
            
        });
    } catch (error) {
        console.error(error)
        throw new Error();
    }
}

function generateYearlyChart(canvas, type, data){
    try {
        new Chart(canvas, {
            type: type,
            data: {
                labels: data.months,
                datasets: [
                    {
                        label: 'Expenses',
                        data: data.expenses,
                        backgroundColor: "rgba(255, 99, 132, 0.6)",
                        borderColor: "rgba(255, 99, 132, 1)",
                        borderWidth: 1
                    },
                    {
                        label: 'incomes',
                        data: data.incomes,
                        backgroundColor: "rgba(75, 192, 192, 0.6)",
                        borderColor: "rgba(75, 192, 192, 1)",
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
    } catch (error) {
        console.error(error);
        throw new Error();
    }
}

function generateYearlyAllModelsChart(canvas, type, data){
    return new Chart(canvas, {
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
    monthlyData = await getMonthlyIncomeAndExpenseData();
    yearlyData = await getYearlyIncomeAndExpenseData();
    generateMontlyChart(monthlyIncomesAndExpensesChart, 'doughnut', monthlyData);
    generateYearlyChart(yearlyIncomesAndExpensesChart, 'bar', yearlyData);

    payload = {
        
    }
    let data = await getData(yearlyStatsAllModelsEndpoint, {year: 2026});
    console.log(data.months);
    generateYearlyAllModelsChart(yearlyStatsAllModelsChart, 'line', data);
});