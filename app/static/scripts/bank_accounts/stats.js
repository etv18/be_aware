const yearlyEndpoint = document.getElementById('yearly-cash-flow-endpoint-id').value;
const yearlyCanvas = document.getElementById('yearly-stats');
const tableCashFlow = document.getElementById('cash-flow-table-id');
const theadCashFlow = tableCashFlow.querySelector('thead');
const tbodyCashFlow = tableCashFlow.querySelector('tbody');

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


function canBeNumberStrict(value) {
    return value !== '' && value !== null && !Number.isNaN(Number(value));
}

function buildRow(label, values, tag){
    let row = '<tr>'; //open row

    row += `<${tag} class="fs-6 fw-bold table-active">${label}</${tag}>`; //this will display the name of the row

    values.forEach(val => {
        const isNumber = canBeNumberStrict(val);
        const numericValue = isNumber ? Number(val) : null;

        let textClass = '';

        if(label.toLowerCase() === 'balances'){
            if(isNumber && numericValue < 0){
                textClass = 'text-danger';
            } else if (isNumber && numericValue > 0){
                textClass = 'text-primary';
            }
        }

        if(!isNumber) textClass += ' table-active';

        row += `
            <${tag} class="${textClass}">
                ${canBeNumberStrict(val) 
                    ? Number(val).toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }) 
                    : val}
            </${tag}>
        `;
    });

    row += '</tr>'; //close row
    return row;
}

function buildCashFlowTable(data){
    theadCashFlow.innerHTML = buildRow('Months', data.months, 'th');
    tbodyCashFlow.innerHTML = `
        ${buildRow('Incomings', data.incomings, 'td')}
        ${buildRow('Outgoings', data.outgoings, 'td')}
        ${buildRow('Balances', data.balances, 'td')}
    `;
}

document.addEventListener('DOMContentLoaded', async e => {
    var data = await getYearlyCashFlowData();
    await generateYearlyChart(yearlyCanvas, 'bar', data);
    buildCashFlowTable(data);
});