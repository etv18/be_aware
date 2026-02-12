const monthlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-monthly');
const yearlyIncomesAndExpensesChart = document.getElementById('incomes-and-expenses-yearly');
const yearlyStatsAllModelsChart = document.getElementById('yearly-stats-all-models');

const selectYearElement = document.getElementById('year-select');

const yearlyStatsAllModelsEndpoint = document.getElementById('yearly-stats-all-models-endpoint').value;
const yearlyCashFlowEndpoint = document.getElementById('yearly-cash-flow-endpoint').value;

let yearlyStatsAllModelsChartInstance = null;
let yearlyIncomesAndOutgoingsChartInstance = null;

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

async function generateMontlyChart(canvas, type, data) {
    try {
        new Chart(canvas, {
            type: type,
            data: {
                labels: ['Incomes', 'Expenses'],
                datasets: [{
                    label: 'Amount',
                    data: [data.incomes, data.expenses],
                    borderWidth: 1,
                    backgroundColor: [
                        '#2563eb', // blue → incomes
                        '#dc2626'  // red → expenses
                    ],
                    borderColor: [
                        '#85a1ff',
                        '#f57777'
                    ],
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

function generateYearlyIncomesAndExpensesChart(canvas, type, data){
if (yearlyIncomesAndOutgoingsChartInstance) {
        yearlyIncomesAndOutgoingsChartInstance.destroy();
    }

    yearlyIncomesAndOutgoingsChartInstance = new Chart(canvas, {
        type: type,
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'Expenses',
                    data: data.report.expenses,
                    backgroundColor: "rgb(243, 0, 53)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    borderWidth: 1
                },
                {
                    label: 'Incomes',
                    data: data.report.incomes,
                    backgroundColor: "rgb(21, 75, 255)",
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
}

function generateYearlyAllModelsChart(canvas, type, data){
if (yearlyStatsAllModelsChartInstance) {
        yearlyStatsAllModelsChartInstance.destroy();
    }

    yearlyStatsAllModelsChartInstance = new Chart(canvas, {
        type: type,
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'Expenses',
                    data: data.report.expenses,
                    backgroundColor: "#dd3445",
                    borderColor: "#dd3445",
                    borderWidth: 1                       
                },
                {
                    label: 'Withdrawals',
                    data: data.report.withdrawals,
                    backgroundColor: "#b9dc88",
                    borderColor: "#b9dc88",
                    borderWidth: 1 
                },
                {
                    label: 'Loans',
                    data: data.report.loans,
                    backgroundColor: "#ffc106",
                    borderColor: "#ffc106",
                    borderWidth: 1 
                },
                {
                    label: 'Credit Card Payments',
                    data: data.report.credit_card_payments,
                    backgroundColor: "#6d747c",
                    borderColor: "#6d747c",
                    borderWidth: 1 
                },
                {
                    label: 'Debt Payments',
                    data: data.report.debt_payments,
                    backgroundColor: "#3a768b",
                    borderColor: "#3a768b",
                    borderWidth: 1 
                },
                {
                    label: 'Loan Payment',
                    data: data.report.loan_payment,
                    backgroundColor: "#198754",
                    borderColor: "#198754",
                    borderWidth: 1 
                },
                {
                    label: 'Incomes',
                    data: data.report.incomes,
                    backgroundColor: "#0d6efd",
                    borderColor: "#0d6efd",
                    borderWidth: 1 
                },
                {
                    label: 'Deposits',
                    data: data.report.deposits,
                    backgroundColor: "#624ea2",
                    borderColor: "#624ea2",
                    borderWidth: 1 
                },
                {
                    label: 'Debts',
                    data: data.report.debts,
                    backgroundColor: "#dfbab1",
                    borderColor: "#dfbab1",
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

function toTitle(str) {
  return str
    .replace(/_/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
}

function canBeNumberStrict(value) {
    return value !== '' && value !== null && !Number.isNaN(Number(value));
}

function buildRow(label, values, tag, options = {}) {
    const {
        rowClass = '',
        labelClass = '',
        cellClass = '',
        classForNonNumberTxt = ''
    } = options;

    let row = `<tr class="${rowClass}">`;

    // LABEL CELL (always text-start)
    row += `
        <${tag} class="fs-6 fw-bold text-start ${labelClass}">
            ${label}
        </${tag}>
    `;

    values.forEach(val => {
        const isNumber = canBeNumberStrict(val);
        const numericValue = isNumber ? Number(val) : null;

        let textClass = '';

        // 🔥 Hardcoded Balances logic (kept as requested)
        if (label.toLowerCase() === 'balances') {
            if (isNumber && numericValue < 0) {
                textClass = 'fw-bold text-danger';
            } else if (isNumber && numericValue > 0) {
                textClass = 'fw-bold text-primary';
            }
        }

        // Content always text-end
        textClass += isNumber
            ? ' text-end'
            : `${classForNonNumberTxt} text-end`;

        // Add custom cell class if provided
        textClass += ` ${cellClass}`;

        row += `
            <${tag} class="${textClass}">
                ${isNumber
                    ? numericValue.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    })
                    : val}
            </${tag}>
        `;
    });

    row += '</tr>';
    return row;
}


function buildYearlyReportTable(data, table){
    table.innerHTML = ""; // reset

    /* ---------- THEAD ---------- */
    const thead = document.createElement("thead");

    thead.classList.add('text-end');
    thead.innerHTML = buildRow('Months', data.months, 'th', {
        rowClass: 'table-primary'
    });

    table.appendChild(thead);

    /* ---------- TBODY ---------- */
    const tbody = document.createElement('tbody');
    for(const key in data.report){
        tbody.innerHTML += `${buildRow(toTitle(key.toString()), data.report[key], 'td', {
                labelClass: 'table-active'
            }
        )}`;
        console.log("Key:", key);
        console.log("Values:", data.report[key]);
    }
    table.appendChild(tbody);
}

function buildCashFlowTable(data, table){
    table.innerHTML = ""; // reset

    /* ---------- THEAD ---------- */
    const thead = document.createElement("thead");    
    thead.innerHTML = buildRow('Months', data.months, 'th', {
        rowClass: 'table-success',
        labelClass: 'table-success'
    });

    table.appendChild(thead);

    /* ---------- TBODY ---------- */
    const tbody = document.createElement('tbody');
    tbody.innerHTML = `
        ${buildRow('Incomes', data.report.incomes, 'td', {
            rowClass: '',
            labelClass: 'table-active'
        })}
        ${buildRow('Expenses', data.report.expenses, 'td', {
            labelClass: 'table-active'
        })}
        ${buildRow('Balances', data.report.balances, 'td', {
            labelClass: 'table-active'
        })}
    `;
    table.appendChild(tbody);
}


document.addEventListener('DOMContentLoaded',async (event) => {
    monthlyData = await getMonthlyIncomeAndExpenseData();
    generateMontlyChart(monthlyIncomesAndExpensesChart, 'doughnut', monthlyData);
    //yearlyData = await getYearlyIncomeAndExpenseData();
    //generateYearlyChart(yearlyIncomesAndExpensesChart, 'bar', yearlyData);

    let years = selectYearElement.options;
    let payload = {year: years[0].value};

    let allModelsData = await getData(yearlyStatsAllModelsEndpoint, payload);
    generateYearlyAllModelsChart(yearlyStatsAllModelsChart, 'line', allModelsData);
    generateYearlyIncomesAndExpensesChart(yearlyIncomesAndExpensesChart, 'bar', allModelsData);
    
    const yearlyReportTable = document.getElementById('yearly-report-table');
    buildYearlyReportTable(
        allModelsData, 
        yearlyReportTable
    );
    
    let cashFlowData = await getData(yearlyCashFlowEndpoint, payload);
    const cashFLowTable = document.getElementById('cash-flow-table');
    buildCashFlowTable(
        cashFlowData, 
        cashFLowTable
    );
});

selectYearElement.addEventListener('change', async (event) => {
    const selectedYear = event.target.value;
    const payload = {
        year: selectedYear
    };

    let allModelsData = await getData(yearlyStatsAllModelsEndpoint, payload);
    generateYearlyAllModelsChart(yearlyStatsAllModelsChart, 'line', allModelsData);
    generateYearlyIncomesAndExpensesChart(yearlyIncomesAndExpensesChart, 'bar', allModelsData);

    const yearlyReportTable = document.getElementById('yearly-report-table');
    buildYearlyReportTable(allModelsData, yearlyReportTable);

    let cashFlowData = await getData(yearlyCashFlowEndpoint, payload);
    const cashFLowTable = document.getElementById('cash-flow-table');
    buildCashFlowTable(cashFlowData, cashFLowTable);
});