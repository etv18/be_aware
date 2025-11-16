/*
best way to compare to undifined values, it only matches expecifically undefined values
if (typeof yourVariable === 'undefined') {...}
*/

const btnSearchByTimeFrame = document.getElementById('btn-search-by-timeframe-id');

let startDate;
let endDate;

const timeRange = flatpickr('#start-date-id', {
    mode: 'range',
    altInput: true,
    altFormat: 'M j, Y',
    dateFormat: 'Y-m-d',
    onChange: (selectedDates, dateStr, instance) => {
        if(selectedDates.length === 2){
            startDate = selectedDates[0];
            endDate = selectedDates[1];
        }
    },
});

function renderExpensesTable(expenses){
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
            <td>${expense.amount.toFixed(2)}</td>
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
                    >Edit</button>
                    <form action="expenses/delete/${expense.id}" method="POST">
                        <button type="submit" class="btn btn-danger">Delete</button>
                    </form>
                </div>
            </td>
        `;
        tbody.appendChild(tableRow);
    });
}

async function getDataFilteredByTime(start, end){
    let data;

    try {
        const response = await fetch(`/expenses/filter_by_time?start=${start}&end=${end}`);
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
            text: err.message || 'Could not connect to server.'
        });
    }

    return data;
}

//Listeners
btnSearchByTimeFrame.addEventListener('click',async () => {
    const start = timeRange.formatDate(startDate, 'Y-m-d');
    const end = timeRange.formatDate(endDate, 'Y-m-d');
    const expenses = await getDataFilteredByTime(start, end);
    renderExpensesTable(expenses);
});

