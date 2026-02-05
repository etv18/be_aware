let yearlyStatsExpenseChartInstance = null; //This it'll be needed to be able to update the chart's data when a user selects a different year

export const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
export const CURRENT_YEAR = new Date().getFullYear();

export async function getData(url, payload) {
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

export function generateYearlyAllModelsChart(canvas, type, label, dataArray, backgroundColor, borderColor){
if (yearlyStatsExpenseChartInstance) {
        yearlyStatsExpenseChartInstance.destroy();
    }

    yearlyStatsExpenseChartInstance = new Chart(canvas, {
        type: type,
        data: {
            labels: MONTHS,
            datasets: [
                {
                    label: label,
                    data: dataArray,
                    backgroundColor: backgroundColor,
                    borderColor: borderColor,
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

