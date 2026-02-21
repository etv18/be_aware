import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";
import {renderDataTable, filterTableData, colSpan, expensesTemplateFn} from '../utils/dynamicTables.js'

const expenseFilterInput = document.getElementById('filter-input-expense-id');
const creditCardPaymentFilterInput = document.getElementById('filter-input-credit-card-payment-id');
const loanFilterInput = document.getElementById('filter-input-loan-id');

const tBodyLoan = document.getElementById('loans-table-body');
const tBodyCreditCardPayment = document.getElementById('credit-card-payment-table-body');
const tBodyExpense = document.getElementById('expenses-table-body');

const creditCardPaymentsTemplateFn = (creditCardPayment) => `
    <th scope="row">${ creditCardPayment.id }</th>
    <td class="text-start">${ formatNumber(creditCardPayment.amount) }</td>
    <td>${ creditCardPayment.credit_card_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.bank_account_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.created_at }</td>
    <td class="d-flex justify-content-center">
        <div class="d-flex gap-2">
            <button 
                type="button" 
                class="btn btn-outline-success" 
                data-bs-toggle="modal" 
                data-bs-target="#edit-credit-card-payment"
                data-endpoint="/credit_card_payments/update/${creditCardPayment.id}"
                data-credit-card-payment-id="${ creditCardPayment.id }"
                data-amount="${ creditCardPayment.amount }"
                data-credit-card-id="${ creditCardPayment.credit_card_id }"
                data-bank-account-id="${ creditCardPayment.bank_account_id }"
            >
                <i class="bi bi-pen"></i>
            </button>
            <a href="/credit_card_payments/delete/${ creditCardPayment.id }" class="btn btn-danger"><i class="bi bi-trash"></i></a>
        </div>
    </td>
`;

const loansTemplateFn = (loan) => `
    <th scope="row">${loan.id}</th>
    <td class="text-start">${formatNumber(loan.amount)}</td>
    <td>${loan.person_name ?? '-'}</td>
    <td> ${formatNumber(loan.remaining_amount)} </td>
    <td>${loan.is_active ? '<span class="badge text-bg-primary">ACTIVE</span>' : '<span class="badge text-bg-success">PAID</span>'}</td>
    <td class="text-start">${loan.description ?? '-'}</td>
    <td>${loan.credit_card_nick_name ?? '-'}</td>
    <td>${loan.created_at}</td>
`;

let data;

async function getAssociatedRecords() {
    const endpoint = document.getElementById('associated-records-endpoint-id').textContent;
    try {
        const response = await fetch(endpoint);
        
        if(!response.ok){
            console.log(response.json());
            return;           
        }
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error('Fetch error: ', error);  
    }
}

document.addEventListener('DOMContentLoaded', async e => {
    data = await getAssociatedRecords();
});

expenseFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-expenses-id');
        const totalCount = document.getElementById('total-count-expenses-id');

        var query = expenseFilterInput.value;

        const filteredList = filterTableData(data.records.expenses ?? [], query);
        renderDataTable(filteredList, tBodyExpense, expensesTemplateFn, colSpan.EXPENSES);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);

creditCardPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-credit-card-payments-id');
        const totalCount = document.getElementById('total-count-credit-card-payments-id');

        var query = creditCardPaymentFilterInput.value;

        const filteredList = filterTableData(data.records.credit_card_payments, query);

        renderDataTable(filteredList, tBodyCreditCardPayment, creditCardPaymentsTemplateFn, colSpan.CREDIT_CARD_PAYMENTS);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;

    })
);

loanFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-loans-id');
        const totalCount = document.getElementById('total-count-loans-id');
        var query = loanFilterInput.value;

        const filteredList = filterTableData(data.records.loans, query);

        renderDataTable(filteredList, tBodyLoan, loansTemplateFn, colSpan.LOANS);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
        totalCount.textContent = `RECORDS: ${filteredList.length}`;
    })
);



