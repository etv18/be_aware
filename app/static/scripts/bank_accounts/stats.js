import { getData, CURRENT_YEAR } from '../utils/generateChart.js';

const yearlyCashFlowEndPoint = document.getElementById('yearly-cash-flow-endpoint-id').value;
const yearlyTotalPerAssociationEndPoint = document.getElementById('yearly-total-per-association-endpoint-id').value;
const yearlyCashFlowCanvas = document.getElementById('yearly-stats');
const yearlyTotalPerAssociationCanvas = document.getElementById('yearly-total-per-association-chart');
const tableCashFlow = document.getElementById('cash-flow-table-id');
const theadCashFlow = tableCashFlow.querySelector('thead');
const tbodyCashFlow = tableCashFlow.querySelector('tbody');
const yearSelect = document.getElementById('year-select');

const yearlyAllModelsYearSpan = document.getElementById('yearly-all-models-year-span');
const yearlyCashFlowYearSpan = document.getElementById('yearly-cash-flow-year-span');

/*-------------------------------------------------------------------------------------------------*/
/* This it'll be needed to be able to update the chart's data when a user selects a different year */
let yearlyLineChartInstance = null; 
let yearlyBarChartInstance = null; 
/*-------------------------------------------------------------------------------------------------*/
function generateYearlyCashFlowChart(canvas, type, data){
    try {
    if (yearlyBarChartInstance) {
        yearlyBarChartInstance.destroy();
    }

    yearlyBarChartInstance =  new Chart(canvas, {
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
        if (yearlyLineChartInstance) {
            yearlyLineChartInstance.destroy();
        }

        yearlyLineChartInstance = new Chart(canvas, {
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
        ${buildRow('Incomes', data.incomes, 'td')}
        ${buildRow('Expenses', data.expenses, 'td')}
        ${buildRow('Balances', data.balances, 'td')}
    `;
}

document.addEventListener('DOMContentLoaded', async e => {
    let payload = {
        "bank_account_id": 19,
        "year": CURRENT_YEAR
    }
    var data = await getData(yearlyCashFlowEndPoint, payload);
    await generateYearlyCashFlowChart(yearlyCashFlowCanvas, 'bar', data);
    buildCashFlowTable(data);

    data = await getData(yearlyTotalPerAssociationEndPoint, payload);
    await generateYearlyTotalPerAssociationChart(yearlyTotalPerAssociationCanvas, 'line', data);

    yearlyAllModelsYearSpan.textContent = CURRENT_YEAR.toString();
    yearlyCashFlowYearSpan.textContent = CURRENT_YEAR.toString();
});

yearSelect.addEventListener('change', async (event) => {
    const selectedYear = event.target.value;
    let payload = {
        "bank_account_id": 19,
        "year": selectedYear
    }
    var data = await getData(yearlyCashFlowEndPoint, payload);
    await generateYearlyCashFlowChart(yearlyCashFlowCanvas, 'bar', data);
    buildCashFlowTable(data);

    data = await getData(yearlyTotalPerAssociationEndPoint, payload);
    await generateYearlyTotalPerAssociationChart(yearlyTotalPerAssociationCanvas, 'line', data);

    yearlyAllModelsYearSpan.textContent = selectedYear.toString();
    yearlyCashFlowYearSpan.textContent = selectedYear.toString();
});