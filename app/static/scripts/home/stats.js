const canvas = document.getElementById('incomes-and-expenses');

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

async function generateChart() {
    data = await getIncomeAndExpenseData();
    console.log(data.expenses)
    console.log(data.incomes)
    try {
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['Incomes', 'Expenses'],
                datasets: [{
                    label: '# of Votes',
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

document.addEventListener('DOMContentLoaded', (event) => generateChart())