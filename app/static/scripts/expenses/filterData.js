/*
best way to compare to undifined values, it only matches expecifically undefined values
if (typeof yourVariable === 'undefined') {...}
*/

const selectFilterType = document.getElementById('select-filter-type-id');
const filterInput = document.getElementById('filter-input-id');
const btnSearch = document.getElementById('btn-search-id');

let timePicker = null;
let startDate = null;
let endDate = null;

export function renderExpensesTable(expenses){
    const tbody = document.getElementById('expenses-table-body');
    tbody.innerHTML = ''; //first you must clear previous rows

    if(expenses.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted">No expenses found for this date range.</td>
            </tr>  
        `;
        return;
    }

    expenses.forEach(expense => {
        const tableRow = document.createElement('tr');
        tableRow.innerHTML = `
            <th scope="row">${expense.id}</th>
            <td>${expense.amount}</td>
            <td>${expense.is_cash ? 'Yes' : 'No'}</td>
            <td>${expense.description || '-'}</td>
            <td>${expense.credit_card_name || '-'}</td>
            <td>${expense.bank_account_name || '-'}</td>
            <td>${expense.expense_category_name || '-'}</td>
            <td>${new Date(expense.created_at).toLocaleString()}</td>
            <td>
                <div class="d-flex gap-2">
                    <button 
                        type="button"
                        class="btn btn-success"
                        data-bs-toggle="modal"
                        data-bs-target="#edit-expense"
                        data-expense-id="${expense.id}"
                        data-amount-id="${expense.amount}"
                        data-is-cash="${expense.is_cash}"
                        data-select-expense-category-id="${expense.expense_category_id}"
                        data-select-credit-card-id="${expense.credit_card_id}"
                        data-select-bank-account-id="${expense.bank_account_id}"
                        data-description="${expense.description}"
                    >Edit</button>
                    <a href="/expenses/delete/${expense.id}" class="btn btn-danger">Delete</a>
                </div>
            </td>
        `;
        tbody.appendChild(tableRow);
    });
}

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
    let url = '';
    if(selectFilterType.value === 'field'){
        url = `/expenses/filter_by_field?query=${filterInput.value}`;
    } else {
        if(startDate === null || endDate === null){ 
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'You need to select two dates.'
            });
            return;
        }  
        const start = timePicker.formatDate(startDate, 'Y-m-d');      
        const end = timePicker.formatDate(endDate, 'Y-m-d'); 

        url = `/expenses/filter_by_time?start=${start}&end=${end}`;
    }

    const data = await getData(url);

    renderExpensesTable(data.expenses);

    //startDate = null;
    //endDate = null;
}

//LISTENERS
selectFilterType.addEventListener('change', e => {
    if(e.target.value == 'time'){
        timePicker = flatpickr(filterInput, {
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
        return;  
    }

    if(timePicker){
        timePicker.destroy();
        timePicker = null;
    }

    filterInput.type = "text";
    filterInput.value = "";
});


btnSearch.addEventListener('click', async e => {
    await filterData();
});

filterInput.addEventListener('keydown', debounce(async e => {
    if(selectFilterType.value !== 'field' && e.key !== 'Enter') return;
    await filterData();
}));