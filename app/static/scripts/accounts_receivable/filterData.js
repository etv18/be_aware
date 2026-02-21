import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";


const filterByFieldInput = document.getElementById('filter-byfiled-input-id');
const filterByTimeInput = document.getElementById('filter-bytime-input-id');
const btnSearch = document.getElementById('btn-search-id');
const lblTotalLoans = document.getElementById('total-loans-id');
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


function renderDataTable(loans){
    const tbody = document.getElementById('loans-table-body-id');
    tbody.innerHTML = '';

    if(loans.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="11" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }

    loans.forEach(loan => {
        const tableRow = document.createElement('tr');

        tableRow.classList.add('loan-row');

        tableRow.setAttribute('data-loan-id', loan.id)
        tableRow.setAttribute('data-url-associated-records', `/accounts_receivable/associated_records/${loan.id}`);

        tableRow.innerHTML = `
            <th scope="row">${loan.id}</th>
            <td>${loan.person_name}</td>
            <td>${formatNumber(loan.amount)}</td>
            <td> ${formatNumber(loan.remaining_amount)} </td>
            <td>
                ${
                    loan.is_active ? '<span class="badge text-bg-primary">ACTIVE</span>' : '<span class="badge text-bg-success">PAID</span>'
                }
            </td>
            <td>${loan.description}</td>
            <td>
                ${
                    loan.is_cash ? '<span class="badge text-bg-light">YES</span>' : '<span class="badge text-bg-secondary">NO</span>'
                }
            </td>
            <td>${loan.credit_card_nick_name}</td>
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
                        <i class="bi bi-cash-coin"></i>
                    </button>
                    <button 
                        type="button" 
                        class="btn btn-outline-success" 
                        data-bs-toggle="modal" 
                        data-bs-target="#edit-account-receivable"
                        data-loan-id="${loan.id}"
                        data-amount="${loan.amount}"
                        data-is-cash="${loan.is_cash}"
                        data-is-active="${loan.is_active}"
                        data-description="${loan.description}"
                        data-person-name="${loan.person_name}"
                        data-bank-account-id="${loan.bank_account_id}"
                        data-credit-card-id="${loan.credit_card_id}"
                    >
                        <i class="bi bi-pen"></i>
                    </button>
                    <a href="/accounts_receivable/delete/${loan.id}" class="btn btn-danger"> <i class="bi bi-trash"></i></a>
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

    renderDataTable(data.loans);

    lblTotalLoans.textContent = 'Total: $' + data.total;

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

filterInput.addEventListener('keydown', debounce(async e => {
    if(selectFilterType.value !== 'field' && e.key !== 'Enter') return;
    await filterData();
}));

