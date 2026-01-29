const yearlyExpenseChart = document.getElementById('yearly-stats-expense');
const yearlySingleModelReportEndpoint = document.getElementById('yearly-single-model-report-endpoint').value;

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