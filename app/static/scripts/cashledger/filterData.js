import { debounce } from "../utils/asyncHanlding.js";
import { titleCase } from "../utils/stringHandling.js";
import { formatNumber } from "../utils/numericHandling.js";

const filterByTimeInput = document.getElementById('filter-bytime-input-id');
const btnSearch = document.getElementById('btn-search-id');
const lblTotal = document.getElementById('lbl-total');
const filterByFieldInput = document.getElementById('filter-byfiled-input-id');
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

function renderDataTable(ledgers){
    const tbody = document.getElementById('cashledger-table-body-id');
    tbody.innerHTML = '';

    if(ledgers.length === 0){
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }

    ledgers.forEach(ledger => {
        const tableRow = document.createElement('tr');

        tableRow.innerHTML = `
            <th scope="row">${ ledger.id }</th>
            <td class="text-start">${ ledger.reference_code }</td>
            <td class="text-start">${ titleCase(ledger.type) }</td>
            <td class="text-start">${ formatNumber(ledger.amount) }</td>
            <td>${ ledger.created_at }</td>
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

    renderDataTable(data.ledgers);

    lblTotal.textContent = 'Total: $'+ data.total;
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