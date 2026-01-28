import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";

const filterByFieldInput = document.getElementById('filter-byfiled-input-id');
const filterByTimeInput = document.getElementById('filter-bytime-input-id');
const btnSearch = document.getElementById('btn-search-id');
const lblTotal = document.getElementById('lbl-total-deposits');
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

function renderDataTable(deposits){
    const tbody = document.getElementById('deposit-table-body-id');
    tbody.innerHTML = '';

    if(deposits.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }

    deposits.forEach(deposit => {
        const tableRow = document.createElement('tr');
        
        tableRow.innerHTML = `
            <th scope="row">${ deposit.id }</th>
            <td>${ formatNumber(deposit.amount) }</td>
            <td>${ deposit.description ? deposit.description : '-'}</td>
            <td>${ deposit.bank_account_nick_name }</td>
            <td>${ deposit.created_at }</td>
            <td>
                <div class="d-flex gap-2">
                    <button 
                        type="button" 
                        class="btn btn-outline-success" 
                        data-bs-toggle="modal" 
                        data-bs-target="#edit-deposit-modal"
                        data-deposit-id="${ deposit.id }"
                        data-description="${ deposit.description }"
                        data-amount="${ deposit.amount }"
                        data-bank-account-id="${ deposit.bank_account_id }"
                    >
                    <i class="bi bi-pen"></i>
                    </button>
                    <a href="/deposits/delete/${deposit.id}" class="btn btn-danger"><i class="bi bi-trash"></i></a>
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

    renderDataTable(data.deposits);

    lblTotal.textContent = 'Total Deposits: $'+ data.total;
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