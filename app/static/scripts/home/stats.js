const monthlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-monthly');
const yearlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-yearly');

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

document.addEventListener('DOMContentLoaded',async (event) => {
    monthlyData = await getMonthlyIncomeAndExpenseData();
    yearlyData = await getYearlyIncomeAndExpenseData();
    generateMontlyChart(monthlyIncomesAndExpensesChart, 'doughnut', monthlyData);
    generateYearlyChart(yearlyIncomesAndExpensesChart, 'bar', yearlyData);
});