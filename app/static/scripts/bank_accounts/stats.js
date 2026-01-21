const yearlyCashFlowEndPoint = document.getElementById('yearly-cash-flow-endpoint-id').value;
const yearlyTotalPerAssociationEndPoint = document.getElementById('yearly-total-per-association-endpoint-id').value;
const yearlyCashFlowCanvas = document.getElementById('yearly-stats');
const yearlyTotalPerAssociationCanvas = document.getElementById('yearly-total-per-association-chart');
const tableCashFlow = document.getElementById('cash-flow-table-id');
const theadCashFlow = tableCashFlow.querySelector('thead');
const tbodyCashFlow = tableCashFlow.querySelector('tbody');

async function getData(endpoint){
    try {
        response = await fetch(endpoint);
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

function generateYearlyCashFlowChart(canvas, type, data){
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

function generateYearlyTotalPerAssociationChart(canvas, type, data){
    try {
        new Chart(canvas, {
            type: type,
            data: {
                labels: data.months,
                datasets: [
                    {
                        label: 'Expenses',
                        data: data.associations_info.expenses,
                        backgroundColor: "#dd3445",
                        borderColor: "#dd3445",
                        borderWidth: 1                       
                    },
                    {
                        label: 'Withdrawals',
                        data: data.associations_info.withdrawals,
                        backgroundColor: "#b9dc88",
                        borderColor: "#b9dc88",
                        borderWidth: 1 
                    },
                    {
                        label: 'Loans',
                        data: data.associations_info.loans,
                        backgroundColor: "#ffc106",
                        borderColor: "#ffc106",
                        borderWidth: 1 
                    },
                    {
                        label: 'Credit Card Payments',
                        data: data.associations_info.credit_card_payments,
                        backgroundColor: "#6d747c",
                        borderColor: "#6d747c",
                        borderWidth: 1 
                    },
                    {
                        label: 'Debt Payments',
                        data: data.associations_info.debt_payments,
                        backgroundColor: "#3a768b",
                        borderColor: "#3a768b",
                        borderWidth: 1 
                    },
                    {
                        label: 'Loan Payment',
                        data: data.associations_info.loan_payment,
                        backgroundColor: "#198754",
                        borderColor: "#198754",
                        borderWidth: 1 
                    },
                    {
                        label: 'Incomes',
                        data: data.associations_info.incomes,
                        backgroundColor: "#0d6efd",
                        borderColor: "#0d6efd",
                        borderWidth: 1 
                    },
                    {
                        label: 'Deposits',
                        data: data.associations_info.deposits,
                        backgroundColor: "#624ea2",
                        borderColor: "#624ea2",
                        borderWidth: 1 
                    },
                    {
                        label: 'Debts',
                        data: data.associations_info.debts,
                        backgroundColor: "#dfbab1",
                        borderColor: "#dfbab1",
                        borderWidth: 1 
                    },
                    {
                        label: 'Outgoing Transfers',
                        data: data.associations_info.outgoing_transfers,
                        backgroundColor: "#ff8daf",
                        borderColor: "#ff8daf",
                        borderWidth: 1 
                    },
                    {
                        label: 'Incoming Transfers',
                        data: data.associations_info.incoming_transfers,
                        backgroundColor: "#86acff",
                        borderColor: "#86acff",
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
    var data = await getData(yearlyCashFlowEndPoint);
    await generateYearlyCashFlowChart(yearlyCashFlowCanvas, 'bar', data);
    buildCashFlowTable(data);

    data = await getData(yearlyTotalPerAssociationEndPoint);
    await generateYearlyTotalPerAssociationChart(yearlyTotalPerAssociationCanvas, 'line', data)
});