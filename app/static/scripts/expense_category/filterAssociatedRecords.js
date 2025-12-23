import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";
import {renderDataTable, filterTableData, colSpan, expensesTemplateFn} from '../utils/dynamicTables.js'

const expenseFilterInput = document.getElementById('filter-input-expense-id');
const tBodyExpense = document.getElementById('expenses-table-body');

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
        var query = expenseFilterInput.value;

        const filteredList = filterTableData(data.records.expenses ?? [], query);
        renderDataTable(filteredList, tBodyExpense, expensesTemplateFn, colSpan.EXPENSES);
        totatAmounts.textContent = formatNumber(getTotalSumOfAmounts(filteredList));
    })
);
