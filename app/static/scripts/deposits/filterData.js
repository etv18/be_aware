import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";

const selectFilterType = document.getElementById('select-filter-type-id');
const filterInput = document.getElementById('filter-input-id');
const btnSearch = document.getElementById('btn-search-id');
const lblTotal = document.getElementById('lbl-total-deposits');
let timePicker = null;
let startDate = null;
let endDate = null;

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
        url = `/deposits/filter/by/field?query=${filterInput.value}`;
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

        url = `/deposits/filter/by/time?start=${start}&end=${end}`;
    }

    const data = await getData(url);

    renderDataTable(data.deposits);

    lblTotal.textContent = 'Total Deposits: $'+ data.total;
    //startDate = null;
    //endDate = null;
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