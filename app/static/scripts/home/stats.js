const monthlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-monthly');
const yearlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-yearly');

async function getIncomeAndExpenseData(){
    try {
        const response = await fetch('/home/populate_expense_and_income_chart');
        if(!response.ok) {
            console.log(response);
            return;
        }
        const data = await response.json();

        return data;
    } catch (error) {
        console.error(error);
    }
    return null;
}

async function generateChart(canvas, type) {
    data = await getIncomeAndExpenseData();

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

document.addEventListener('DOMContentLoaded', (event) => {
    generateChart(monthlyIncomesAndExpensesChart, 'doughnut');
    generateChart(yearlyIncomesAndExpensesChart, 'bar');
});