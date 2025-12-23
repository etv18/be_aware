import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";
import {renderDataTable, filterTableData, colSpan } from '../utils/dynamicTables.js'

const tBodyLoanPayment = document.getElementById('loan-payment-table-body');
const loanPaymentFilterInput = document.getElementById('filter-input-loan-payment-id');
let data;

const loanPaymentsTemplateFn = (loanPayment) => `
    <th scope="row">${ loanPayment.id }</th>
    <td class="text-start">${ loanPayment.amount }</td>
    <td>${ loanPayment.is_cash ? 'YES' : 'NO' }</td>
    <td>${ loanPayment.bank_account_nick_name ?? '-'}</td>
    <td>${ loanPayment.created_at }</td>
    <td>
        <div class="d-flex gap-2 justify-content-center">
            <button 
                type="button" 
                class="btn btn-success" 
                data-bs-toggle="modal" 
                data-bs-target="#edit-loan-payment"
                data-endpoint="/accounts_receivable/update_loan_payment/${ loanPayment.id }"
                data-loan-id="${ loanPayment.loan_id }"
                data-loan-payment-id="${ loanPayment.id }"
                data-amount="${ loanPayment.amount }"
                data-is-cash="${ loanPayment.is_cash }"
                data-bank-account-id="${ loanPayment.bank_account_id }"
            >
            Edit
            </button>
            <a href="/accounts_receivable/delete_loan_payment/${loanPayment.id}" class="btn btn-danger">Delete</a>
        </div>
    </td>
`;

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
})

loanPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-loans-payments-id');
        var query = loanPaymentFilterInput.value;
        const filteredList = filterTableData(data.records.loan_payment, query);

        renderDataTable(filteredList, tBodyLoanPayment, loanPaymentsTemplateFn, colSpan.LOAN_PAYMENTS);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`)
    })
);