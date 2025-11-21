const canvas = document.getElementById('totals-per-category');

async function getDataByCategory(){
    let data;
    try {
        const response = await fetch(`/expense_categories/monthly/chart`);
        if(!response.ok) {
            console.log(response.json());
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Somethig went wrong while editing the expense.'
            });
            return;
        }

        data = response.json()
    } catch (error) {
        console.error(error);
    }

    return data;
}

function generateMontlyChart(canvas, type, data) {
    try {
        new Chart(canvas, {
            type: type,
            data: {
                labels: data.names,
                datasets: [{
                    label: 'Amount',
                    data: data.totals,
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

document.addEventListener('DOMContentLoaded',async e => {
    data = await getDataByCategory();
    generateMontlyChart(canvas, 'doughnut', data);
});

