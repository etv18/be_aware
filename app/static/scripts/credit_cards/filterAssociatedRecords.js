import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";
import {renderDataTable, filterTableData, colSpan, creditCardPaymentsTemplateFn, expensesTemplateFn} from '../utils/dynamicTables.js'

const expenseFilterInput = document.getElementById('filter-input-expense-id');
const tBodyExpense = document.getElementById('expenses-table-body');

let records;

async function getAssociatedRecords() {
    const endpoint = document.getElementById('associated-records-endpoint-id').textContent;
    try {
        const response = await fetch(endpoint);
        const data = await response.json();

        if(!response.ok){
            console.log(response.json());
            return;           
        }

        return data;
    } catch (error) {
        console.error('Fetch error: ', error);  
    }
}

document.addEventListener('DOMContentLoaded', async e => {
    records = await getAssociatedRecords();
});

expenseFilterInput.addEventListener('input', debounce(async e => {
        const totatAmounts = document.getElementById('total-amounts-expenses-id');
        var query = expenseFilterInput.value;

        const filteredList = filterTableData(records.expenses, query);
        renderDataTable(filteredList, tBodyExpense, expensesTemplateFn, colSpan.EXPENSES);
        totatAmounts.textContent = formatNumber(getTotalSumOfAmounts(filteredList));
    })
);



