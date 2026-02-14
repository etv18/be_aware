import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";
import {renderDataTable, filterTableData, colSpan } from '../utils/dynamicTables.js'

const tBodyDebtPayment = document.getElementById('debt-payment-table-body');
const debtPaymentFilterInput = document.getElementById('filter-input-debt-payment-id');
let data;

const debtPaymentsTemplateFn = (debtPayment) => `
    <th scope="row">${ debtPayment.id }</th>
    <td class="text-start">${ debtPayment.amount }</td>
    <td>
        ${
            debtPayment.is_cash ? '<span class="badge text-bg-light">YES</span>' : '<span class="badge text-bg-secondary">NO</span>'
        }
    </td>
    <td class="text-start">${ debtPayment.bank_account_nick_name ?? '-'}</td>
    <td>${ debtPayment.created_at }</td>
    <td>
        <div class="d-flex gap-2 justify-content-center">
            <button 
                type="button" 
                class="btn btn-outline-success" 
                data-bs-toggle="modal" 
                data-bs-target="#edit-debt-payment"
                data-endpoint="/debt_payments/update/${ debtPayment.id }"
                data-debt-id="${ debtPayment.debt_id }"
                data-debt-payment-id="${ debtPayment.id }"
                data-amount="${ debtPayment.amount }"
                data-is-cash="${ debtPayment.is_cash }"
                data-bank-account-id="${ debtPayment.bank_account_id }"
            >
                <i class="bi bi-pen"></i>
            </button>
            <a href="/debt_payments/delete/${debtPayment.id}" class="btn btn-danger"><i class="bi bi-trash"></i></a>
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

debtPaymentFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-debts-payments-id');
        const totalCount = document.getElementById('total-count-debts-payments-id');
        var query = debtPaymentFilterInput.value;
        const filteredList = filterTableData(data.records.debt_payments, query);

        renderDataTable(filteredList, tBodyDebtPayment, debtPaymentsTemplateFn, colSpan.LOAN_PAYMENTS);
        totatAmounts.textContent = (`TOTAL: ${formatNumber(getTotalSumOfAmounts(filteredList))}`);
        totalCount.textContent = `COUNT: ${filteredList.length}`;
    })
);