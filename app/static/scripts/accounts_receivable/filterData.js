const selectFilterType = document.getElementById('select-filter-type-id');
const filterInput = document.getElementById('filter-input-id');
const btnSearch = document.getElementById('btn-search-id');
let timePicker = null;
let startDate;
let endDate;

function renderDataTable(loans){
    const tbody = document.getElementById('loans-table-body-id');
    tbody.innerHTML = '';

    if(loans.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }

    loans.forEach(loan => {
        const tableRow = document.createElement('tr');
        tableRow.innerHTML = `
            <tr class="loan-row" data-loan-id="${loan.id}" data-url-associated-records = "/accounts_receivable/associated_records/${loan.id}">
                <th scope="row">${loan.id}</th>
                <td>${loan.person_name}</td>
                <td>${loan.amount}</td>
                <td> ${loan.remaining_amount} </td>
                <td>${loan.is_active ? 'ACTIVE' : 'PAID'}</td>
                <td>${loan.description}</td>
                <td>${loan.is_cash ? 'YES' : 'NO'}</td>
                <td>${loan.bank_account_nick_name}</td>
                <td>${loan.created_at}</td>
                <td>
                    <div class="d-flex gap-2">
                        <button 
                            id=""
                            type="button"
                            data-bs-toggle="modal" 
                            data-bs-target="#pay-account-receivable"
                            class="btn btn-outline-light" 
                            data-loan-id="${loan.id}"
                        >
                        Pay
                        </button>
                        <button 
                            type="button" 
                            class="btn btn-success" 
                            data-bs-toggle="modal" 
                            data-bs-target="#edit-account-receivable"
                            data-loan-id="${loan.id}"
                            data-amount="${loan.amount}"
                            data-is-cash="${loan.is_cash}"
                            data-is-active="${loan.is_active}"
                            data-description="${loan.description}"
                            data-person-name="${loan.person_name}"
                            data-bank-account-id="${loan.bank_account_id}"
                        >
                        Edit
                        </button>
                        <a href="/accounts_receivable/delete/${loan.id}" class="btn btn-danger">Delete</a>
                    </div>
                </td>
            </tr>
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
            text: err.message || 'Could not connect to server.'
        });
    }

    return data;
}

selectFilterType.addEventListener('change', (e) => {
    if(e.target.value === 'time'){
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
    const data = await getData(`/accounts_receivable/fiter_loans_by_field?query=${filterInput.value}`);
    renderDataTable(data.loans);
});

