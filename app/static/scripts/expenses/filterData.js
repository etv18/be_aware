import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";

/*
best way to compare to undifined values, it only matches expecifically undefined values
if (typeof yourVariable === 'undefined') {...}
*/

const filterByFieldInput = document.getElementById('filter-byfiled-input-id');
const filterByTimeInput = document.getElementById('filter-bytime-input-id');
const btnSearch = document.getElementById('btn-search-id');
const lblMonthlyTotal = document.getElementById('monthly-total-id');
const filterDataEndpoint = document.getElementById('filter-data-endpoint').value;

let startDate = null;
let endDate = null;

const timePicker = flatpickr(filterByTimeInput, {
    mode: 'range',
    altInput: true,
    altFormat: 'M j, Y',
    dateFormat: 'Y-m-d',
    onChange: (selectedDates, dateStr, instance) => {
        if(selectedDates.length === 2){
            startDate = selectedDates[0];
            endDate = selectedDates[1];
        }
    }
});

export function renderExpensesTable(data){
    const tbody = document.getElementById('expenses-table-body');
    tbody.innerHTML = ''; //first you must clear previous rows

    if(data.expenses.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted">No expenses found for this date range.</td>
            </tr>  
        `;
        return;
    }

    data.expenses.forEach(expense => {
        const tableRow = document.createElement('tr');
        tableRow.innerHTML = `
            <th scope="row">${expense.id}</th>
            <td>${formatNumber(expense.amount)}</td>
            <td>
                ${ expense.is_cash ? '<span class="badge text-bg-light">YES</span>' : '<span class="badge text-bg-secondary">NO</span>' }
            </td>            
            <td>${expense.description || '-'}</td>
            <td>${expense.credit_card_name || '-'}</td>
            <td>${expense.bank_account_name || '-'}</td>
            <td>${expense.expense_category_name || '-'}</td>
            <td>${expense.created_at}</td>
            <td>
                <div class="d-flex gap-2">
                    <button 
                        type="button"
                        class="btn btn-outline-success"
                        data-bs-toggle="modal"
                        data-bs-target="#edit-expense"
                        data-expense-id="${expense.id}"
                        data-amount-id="${expense.amount}"
                        data-is-cash="${expense.is_cash}"
                        data-select-expense-category-id="${expense.expense_category_id}"
                        data-select-credit-card-id="${expense.credit_card_id}"
                        data-select-bank-account-id="${expense.bank_account_id}"
                        data-description="${expense.description}"
                    ><i class="bi bi-pen"></i></button>
                    <a href="/expenses/delete/${expense.id}" class="btn btn-danger"><i class="bi bi-trash"></i></a>
                </div>
            </td>
        `;
        tbody.appendChild(tableRow);
    });

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
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: errorData.error || 'Something went wrong.'
            });
            return;
        }

        data = await response.json();
        console.log(data);

    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: error.message || 'Could not connect to server.'
        });
    }

    return data;
}

async function filterData(){
    let payload = {
        query: null,
        start: null,
        end: null
    };

    if(filterByFieldInput.value.length > 0){
        payload.query = filterByFieldInput.value?.trim() || null;
    }

    payload.start = startDate ? timePicker.formatDate(startDate, 'Y-m-d') : null;
    payload.end = endDate ? timePicker.formatDate(endDate, 'Y-m-d') : null;

    const data = await getData(filterDataEndpoint, payload);

    if (!data) return;

    renderExpensesTable(data);

    lblMonthlyTotal.textContent = 'Total: $'+data.total;

    //startDate = null;
    //endDate = null;
}

btnSearch.addEventListener('click', async e => {
    if(!startDate || !endDate) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'You need to select two dates.'
        });
        return;    
    }
    await filterData();
});

filterByFieldInput.addEventListener('keydown', debounce(async e => {
    if(!filterByFieldInput.value.trim()) return;
    console.log('filterByFieldInput => '+filterByFieldInput.value)
    await filterData();
}));