import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";

//TABLE BODIES
const tBodyExpense = document.getElementById('expenses-table-body');
const tBodyIncome = document.getElementById('incomes-table-body');
const tBodyWithdrawal = document.getElementById('withdrawals-table-body');
const tBodyLoan = document.getElementById('loans-table-body');
const tBodyLoanPayment = document.getElementById('loan-payment-table-body');
const tBodyCreditCardPayment = document.getElementById('credit-card-payment-table-body');
const tBodyBankTransfer = document.getElementById('transfer-table-body');
const tBodyDebt = document.getElementById('debts-table-body');
const tBodyDebtPayment = document.getElementById('debt-payment-table-body');
const tBodyDeposit = document.getElementById('deposits-table-body');

//FILTER INPUTS
const expenseFilterInput = document.getElementById('filter-input-expense-id');
const incomeFilterInput = document.getElementById('filter-input-income-id');
const withdrawalFilterInput = document.getElementById('filter-input-withdrawal-id');
const loanFilterInput = document.getElementById('filter-input-loan-id');
const loanPaymentFilterInput = document.getElementById('filter-input-loan-payment-id');
const creditCardPaymentFilterInput = document.getElementById('filter-input-credit-card-payment-id');
const bankTransferFilterInput = document.getElementById('filter-input-transfer-id');
const debtFilterInput = document.getElementById('filter-input-debt-id');
const debtPaymentFilterInput = document.getElementById('filter-input-debt-payment-id');
const depositFilterInput = document.getElementById('filter-input-withdrawal-id');

const associatedRecordsInJsonEndpoint = document.getElementById('associated-records-url-id').textContent;

let expenses;
let incomes;
let withdrawals;
let loans;
let loanPayments;
let creditCardPayments;
let bankTransfers;
let debts;
let ownerBankAccountId;
let debtPayments;
let deposits;

const colSpan = {
    expenses: 7,
    incomes: 6,
    withdrawals: 5,
    loans: 9,
    loanPayments: 5,
    creditCardPayments: 5,
    bankTransfers: 7
}

const expensesTemplateFn = (expense) => `
    <th scope="row">${expense.id}</th>
    <td class="text-start">${formatNumber(expense.amount)}</td>
    <td class="text-start">${expense.description ?? '-'}</td>
    <td>${expense.bank_account_name ?? '-'}</td>
    <td class="text-start">${expense.expense_category_name ?? '-'}</td>
    <td>${expense.created_at}</td>
`;

const incomesTemplateFn = (income) => `
    <th scope="row">${ income.id }</th>
    <td class="text-start">${ formatNumber(income.amount) }</td>
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
    <td class="text-start">${formatNumber(loan.amount)}</td>
    <td>${loan.person_name ?? '-'}</td>
    <td> ${formatNumber(loan.remaining_amount)} </td>
    <td>${loan.is_active ? '<span class="badge text-bg-primary">ACTIVE</span>' : '<span class="badge text-bg-success">PAID</span>'}</td>
    <td class="text-start">${loan.description ?? '-'}</td>
    <td>${loan.bank_account_nick_name ?? '-'}</td>
    <td>${loan.created_at}</td>
`;

const loanPaymentsTemplateFn = (loanPayment) => `
    <th scope="row">${ loanPayment.id }</th>
    <td class="text-start">${ formatNumber(loanPayment.amount) }</td>
    <td>${ loanPayment.bank_account_nick_name ?? '-'}</td>
    <td>${ loanPayment.created_at }</td>
`;

const creditCardPaymentsTemplateFn = (creditCardPayment) => `
    <th scope="row">${ creditCardPayment.id }</th>
    <td class="text-start">${ formatNumber(creditCardPayment.amount) }</td>
    <td>${ creditCardPayment.credit_card_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.bank_account_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.created_at }</td>
`;

const bankTransfersTemplateFn = (transfer) => `
    <tr>
        <th scope="row">${ transfer.id }</th>
        <td>${ 
            transfer.to_bank_account_id === ownerBankAccountId 
            ?  `<p class="fs-6 text-primary">${formatNumber(transfer.amount)}</p>`
            : `<p class="fs-6 text-danger">-${formatNumber(transfer.amount)}</p>`
        }</td>                        
        <td>${ transfer.from_bank_account_id === ownerBankAccountId ? '.' : transfer.from_bank_account_nick_name }</td>
        <td>${ transfer.to_bank_account_id === ownerBankAccountId ? '.' : transfer.to_bank_account_nick_name }</td>
        <td>${ transfer.created_at }</td>
        <td>
            ${
                transfer.from_bank_account_id === ownerBankAccountId
                ? 
                    `<div class="d-flex gap-2">
                        <button 
                            type="button" 
                            class="btn btn-outline-success"
                            data-bs-toggle="modal"
                            data-bs-target="#edit-bank-transfer"
                            data-transfer-id="${ transfer.id }"
                            data-amount="${ transfer.amount }"
                            data-to-bank-account-id="${ transfer.to_bank_account_id }"
                            data-nick-name="${ transfer.from_bank_account_nick_name }"
                            data-update-endpoint = "/banktransfer/update/${transfer.id}"
                        >
                            <i class="bi bi-pen"></i>
                        </button>
                        <a href="/banktransfer/delete/${transfer.id}" class="btn btn-danger"><i class="bi bi-trash"></i></a>
                    </div>`
                :
                `<p class="fs-6">Not Allowed</p>`                             
            }
        </td>
    </tr>
`;

const debtsTemplateFn = (debt) => `
    <th scope="row">${debt.id}</th>
    <td class="text-start">${formatNumber(debt.amount)}</td>
    <td>${debt.person_name ?? '-'}</td>
    <td> ${formatNumber(debt.remaining_amount)} </td>
    <td>${debt.is_active ? '<span class="badge text-bg-primary">ACTIVE</span>' : '<span class="badge text-bg-success">PAID</span>'}</td>
    <td class="text-start">${debt.description ?? '-'}</td>
    <td>${debt.bank_account_nick_name ?? '-'}</td>
    <td>${debt.created_at}</td>
`;

const debtPaymentsTemplateFn = (debtPayment) => `
    <th scope="row">${ debtPayment.id }</th>
    <td class="text-start">${ formatNumber(debtPayment.amount) }</td>
    <td>${ debtPayment.bank_account_nick_name ?? '-'}</td>
    <td>${ debtPayment.created_at }</td>
`;

const depositsTemplateFn = (deposit) => `
    <th scope="row">${ deposit.id }</th>
    <td>${ formatNumber(deposit.amount) }</td>
    <td>${ deposit.description ?? '-'}</td>
    <td>${ deposit.bank_account_nick_name ?? '-' }</td>
    <td>${ deposit.created_at }</td>
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
        bankTransfers = data.records?.bank_transfers ?? [];
        debts = data.records?.debts ?? [];
        debtPayments = data.records?.debt_payments ?? [];
        deposits = data.records?.deposits ?? [];

        ownerBankAccountId = data.owner_bank_account_id;

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

function filterTransfersByInAndOut(dataSet, query){
    if(query === null || query === undefined || query === '') {
        return dataSet;
    }

    var fields = getKeysFromDataSet(dataSet);

    if(fields.length === 0) return dataSet;

    var term = query.toLowerCase(); //User input

    var filteredList = [];

    dataSet.forEach(item => {
        if(term === 'in'){

            if(item.to_bank_account_id === ownerBankAccountId){ 
                filteredList.push(item);
            }

        } else {

            if(item.to_bank_account_id !== ownerBankAccountId){ 
                filteredList.push(item);
            }
        }
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
        const totalCount = document.getElementById('total-count-expenses-id');
        var query = expenseFilterInput.value;

        const filteredList = filterTableData(expenses, query);

        renderDataTable(filteredList, tBodyExpense, expensesTemplateFn, colSpan.expenses);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`);
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

incomeFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-incomes-id');
        const totalCount = document.getElementById('total-count-incomes-id');
        var query = incomeFilterInput.value;

        const filteredList = filterTableData(incomes, query);

        renderDataTable(filteredList, tBodyIncome, incomesTemplateFn, colSpan.incomes);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`);
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

withdrawalFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-withdrawal-id');
        const totalCount = document.getElementById('total-count-withdrawal-id');
        var query = withdrawalFilterInput.value;

        const filteredList = filterTableData(withdrawals, query);

        renderDataTable(filteredList, tBodyWithdrawal, withdrawalsTemplateFn, colSpan.withdrawals);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

loanFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-loans-id');
        const totalCount = document.getElementById('total-count-loans-id');
        var query = loanFilterInput.value;

        const filteredList = filterTableData(loans, query);

        renderDataTable(filteredList, tBodyLoan, loansTemplateFn, colSpan.loans);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

loanPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-loans-payments-id');
        const totalCount = document.getElementById('total-count-loans-payments-id');
        var query = loanPaymentFilterInput.value;

        const filteredList = filterTableData(loanPayments, query);

        renderDataTable(filteredList, tBodyLoanPayment, loanPaymentsTemplateFn, colSpan.loanPayments);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

creditCardPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-credit-card-payments-id');
        const totalCount = document.getElementById('total-count-credit-card-payments-id');
        var query = creditCardPaymentFilterInput.value;

        const filteredList = filterTableData(creditCardPayments, query);

        renderDataTable(filteredList, tBodyCreditCardPayment, creditCardPaymentsTemplateFn, colSpan.creditCardPayments);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

bankTransferFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-transfers-id');
        const totalCount = document.getElementById('total-count-transfers-id');

        var query = bankTransferFilterInput.value;
        var filteredList;
        if(query.toLowerCase() === 'in' || query.toLowerCase() === 'out'){
            filteredList = filterTransfersByInAndOut(bankTransfers, query);
        } else {
            filteredList = filterTableData(bankTransfers, query);
        }

        renderDataTable(filteredList, tBodyBankTransfer, bankTransfersTemplateFn, colSpan.bankTransfers);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

debtFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-debts-id');
        const totalCount = document.getElementById('total-count-debts-id');
        var query = debtFilterInput.value;

        const filteredList = filterTableData(debts, query);

        renderDataTable(filteredList, tBodyDebt, debtsTemplateFn, colSpan.loans);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

debtPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-debt-payments-id');
        const totalCount = document.getElementById('total-count-debt-payments-id');
        var query = debtPaymentFilterInput.value;

        const filteredList = filterTableData(debtPayments, query);

        renderDataTable(filteredList, tBodyDebtPayment, debtPaymentsTemplateFn, colSpan.loanPayments);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

depositFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-deposit-id');
        const totalCount = document.getElementById('total-count-deposit-id');
        var query = depositFilterInput.value;

        const filteredList = filterTableData(deposits, query);

        renderDataTable(filteredList, tBodyDeposit, depositsTemplateFn, colSpan.withdrawals);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);