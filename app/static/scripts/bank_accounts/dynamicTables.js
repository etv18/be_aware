import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";

//TABLE BODIES
const tBodyExpense = document.getElementById('expenses-table-body');
const tBodyIncome = document.getElementById('incomes-table-body');
const tBodyWithdrawal = document.getElementById('withdrawals-table-body');
const tBodyLoan = document.getElementById('loans-table-body');
const tBodyLoanPayment = document.getElementById('loan-payment-table-body');
const tBodyCreditCardPayment = document.getElementById('credit-card-payment-table-body');

//FILTER INPUTS
const expenseFilterInput = document.getElementById('filter-input-expense-id');
const incomeFilterInput = document.getElementById('filter-input-income-id');
const withdrawalFilterInput = document.getElementById('filter-input-withdrawal-id');
const loanFilterInput = document.getElementById('filter-input-loan-id');
const loanPaymentFilterInput = document.getElementById('filter-input-loan-payment-id');
const creditCardPaymentFilterInput = document.getElementById('filter-input-credit-card-payment-id');

const associatedRecordsInJsonEndpoint = document.getElementById('associated-records-url-id').textContent;

let expenses;
let incomes;
let withdrawals;
let loans;
let loanPayments;
let creditCardPayments;

const colSpan = {
    expenses: 7,
    incomes: 6,
    withdrawals: 5,
    loans: 9,
    loanPayments: 5,
    creditCardPayments: 5
}

const expensesTemplateFn = (expense) => `
    <th scope="row">${expense.id}</th>
    <td class="text-start">${formatNumber(expense.amount)}</td>
    <td>${expense.is_cash ? 'YES' : 'NO'}</td>
    <td class="text-start">${expense.description ?? '-'}</td>
    <td>${expense.credit_card_name ?? '-'}</td>
    <td>${expense.bank_account_name ?? '-'}</td>
    <td class="text-start">${expense.expense_category_name ?? '-'}</td>
    <td>${expense.created_at}</td>
`;

const incomesTemplateFn = (income) => `
    <th scope="row">${ income.id }</th>
    <td class="text-start">${ formatNumber(income.amount) }</td>
    <td>${ income.is_cash ? 'YES' : 'NO'}</td>
    <td class="text-start">${ income.description ?? '-' }</td>
    <td>${ income.bank_nick_name ?? '-'}</td>
    <td>${ income.created_at }</td>
`;

const withdrawalsTemplateFn = (withdrawal) => `
    <th scope="row">${ withdrawal.id }</th>
    <td>${ formatNumber(withdrawal.amount) }</td>
    <td>${ withdrawal.description ?? '-'}</td>
    <td>${ withdrawal.bank_account_nick_name ?? '-' }</td>
    <td>${ withdrawal.created_at }</td>
`;

const loansTemplateFn = (loan) => `
    <th scope="row">${loan.id}</th>
    <td class="text-start">${loan.amount}</td>
    <td>${loan.is_cash ? 'YES' : 'NO'}</td>
    <td>${loan.person_name ?? '-'}</td>
    <td> ${loan.remaining_amount} </td>
    <td>${loan.is_active ? 'ACTIVE' : 'PAID'}</td>
    <td class="text-start">${loan.description ?? '-'}</td>
    <td>${loan.bank_account_nick_name ?? '-'}</td>
    <td>${loan.created_at}</td>
`;

const loanPaymentsTemplateFn = (loanPayment) => `
    <th scope="row">${ loanPayment.id }</th>
    <td class="text-start">${ loanPayment.amount }</td>
    <td>${ loanPayment.is_cash ? 'YES' : 'NO' }</td>
    <td>${ loanPayment.bank_account_nick_name ?? '-'}</td>
    <td>${ loanPayment.created_at }</td>
`;

const creditCardPaymentsTemplateFn = (creditCardPayment) => `
    <th scope="row">${ creditCardPayment.id }</th>
    <td class="text-start">${ creditCardPayment.amount }</td>
    <td>${ creditCardPayment.credit_card_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.bank_account_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.created_at }</td>
`;

async function getData(url){
    let data;

    try {
        const response = await fetch(url);
        if(!response.ok) {
            console.log(response.json());
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Something went wrong while creating the expense.'
            });
            return;
        }
        data = await response.json();
        console.log(data);
        
        /*
            The ? operator allows me to access a property and in case is null or undefined it wont throw an error

            ?? (nullish operator) it throws true for null or undefined values. so here it says if it's .expenses is 
            null or undefined assign an empty list.
        */
        expenses = data.records?.expenses ?? []; 
        incomes = data.records?.incomes ?? [];
        withdrawals = data.records?.withdrawals ?? [];
        loans = data.records?.loans ?? [];
        loanPayments = data.records?.loan_payment ?? [];
        creditCardPayments = data.records?.credit_card_payments ?? [];
        
        return data
        
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: error.message || 'Could not connect to server.'
        });
    }
}

function renderDataTable(objList, tbody, templateFunction, colspanValue){
    tbody.innerHTML = '';

    if(!objList || objList.length === 0 || objList === undefined) {
        tbody.innerHTML = `
            <tr>
                <td colspan="${colspanValue}" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }
    console.log( `${objList}`);
    objList.forEach(obj => {
        const tableRow = document.createElement('tr');
        tableRow.innerHTML = templateFunction(obj);
        tbody.appendChild(tableRow)
    });
}

function filterTableData(dataSet, query){
    if(query === null || query === undefined || query === '') {
        return dataSet;
    }

    var fields = getKeysFromDataSet(dataSet);

    if(fields.length === 0) return dataSet;

    var term = query.toLowerCase(); //User input

    var filteredList = [];

    dataSet.forEach(item => {
        var itemMatches = false;

        for(var i = 0; i < fields.length; i++){
            var key = fields[i];
            var value = item[key]; //Looking in the js object

            if(value === null || value === undefined){
                continue;
            }

            var valueAsString = String(value).toLowerCase(); //Value of the data set

            if(valueAsString.indexOf(term) !== -1){
                itemMatches = true;
                break;
            }
        }
        if(itemMatches) filteredList.push(item);
    });

    return filteredList;
}

function getKeysFromDataSet(dataSet){
    if(!Array.isArray(dataSet) || dataSet.length === 0){
        return [];
    }
    return Object.keys(dataSet[0]);
}

document.addEventListener('DOMContentLoaded', async e => {
    await getData(associatedRecordsInJsonEndpoint);
});

expenseFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-expenses-id');
        var query = expenseFilterInput.value;

        const filteredList = filterTableData(expenses, query);
        renderDataTable(filteredList, tBodyExpense, expensesTemplateFn, colSpan.expenses);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
    })
);

incomeFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-incomes-id');
        var query = incomeFilterInput.value;

        const filteredList = filterTableData(incomes, query);
        renderDataTable(filteredList, tBodyIncome, incomesTemplateFn, colSpan.incomes);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
    })
);

withdrawalFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-withdrawal-id');
        var query = withdrawalFilterInput.value;

        const filteredList = filterTableData(withdrawals, query);
        renderDataTable(filteredList, tBodyWithdrawal, withdrawalsTemplateFn, colSpan.withdrawals);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
    })
);

loanFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-loans-id');
        var query = loanFilterInput.value;

        const filteredList = filterTableData(loans, query);
        renderDataTable(filteredList, tBodyLoan, loansTemplateFn, colSpan.loans);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
    })
);

loanPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-loans-payments-id');
        var query = loanPaymentFilterInput.value;

        const filteredList = filterTableData(loanPayments, query);

        renderDataTable(filteredList, tBodyLoanPayment, loanPaymentsTemplateFn, colSpan.loanPayments);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
    })
);

creditCardPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-credit-card-payments-id');
        var query = creditCardPaymentFilterInput.value;

        const filteredList = filterTableData(creditCardPayments, query);
        console.log('raw list: ', creditCardPayments);
        console.log('filtered list: ', creditCardPayments);
        renderDataTable(filteredList, tBodyCreditCardPayment, creditCardPaymentsTemplateFn, colSpan.creditCardPayments);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
    })
);