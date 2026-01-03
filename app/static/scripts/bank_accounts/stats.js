const yearlyEndpoint = document.getElementById('yearly-cash-flow-endpoint-id').value;
const yearlyCanvas = document.getElementById('yearly-stats');

async function getYearlyCashFlowData(){
    try {
        response = await fetch(yearlyEndpoint);
        if(!response.ok) {
            console.log(response.json());
            return;
        }

        const data = await response.json();
        
        return data;
    } catch (error) {
        console.error(error);
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
                        label: 'Outgoings',
                        data: data.outgoings,
                        backgroundColor: "rgba(255, 99, 132, 0.6)",
                        borderColor: "rgba(255, 99, 132, 1)",
                        borderWidth: 1                       
                    },
                    {
                        label: 'Incomings',
                        data: data.incomings,
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

document.addEventListener('DOMContentLoaded', async e => {
    var data = await getYearlyCashFlowData();
    await generateYearlyChart(yearlyCanvas, 'bar', data)
});