import { debounce } from "../utils/asyncHanlding.js";
import { titleCase } from "../utils/stringHandling.js";
import { formatNumber } from "../utils/numericHandling.js";

const selectFilterType = document.getElementById('select-filter-type-id');
const filterInput = document.getElementById('filter-input-id');
const btnSearch = document.getElementById('btn-search-id');
let timePicker = null;
let startDate = null;
let endDate = null;

function renderDataTable(ledgers){
    const tbody = document.getElementById('cashledger-table-body-id');
    tbody.innerHTML = '';

    if(ledgers.length === 0){
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }

    ledgers.forEach(ledger => {
        const tableRow = document.createElement('tr');

        tableRow.innerHTML = `
            <th scope="row">${ ledger.id }</th>
            <td>${ ledger.reference_code }</td>
            <td>${ titleCase(ledger.transaction_type) }</td>
            <td>${ titleCase(ledger.bank_account.nick_name) }</td>
            <td>${ formatNumber(ledger.amount) }</td>
            <td>${ formatNumber(ledger.before_update_balance) }</td>
            <td>${ formatNumber(ledger.after_update_balance) }</td>
            <td>${ ledger.created_at }</td>
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
        url = `/cashledger/filter/cashledger/by/field?query=${filterInput.value}`;
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

        url = `/cashledger/filter/cashledger/by/time?start=${start}&end=${end}`;
    }

    const data = await getData(url);

    renderDataTable(data.ledgers);
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
    await filterData();
});

filterInput.addEventListener('keydown', debounce(async e => {
    if(selectFilterType.value !== 'field' && e.key !== 'Enter') return;
    await filterData();
}));