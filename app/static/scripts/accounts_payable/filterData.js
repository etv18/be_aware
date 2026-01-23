import { getTotalSumOfAmounts, formatNumber } from "../utils/numericHandling.js";
import { debounce } from "../utils/asyncHanlding.js";


const selectFilterType = document.getElementById('select-filter-type-id');
const filterInput = document.getElementById('filter-input-id');
const btnSearch = document.getElementById('btn-search-id');
const lblTotal = document.getElementById('lbl-total');

let timePicker = null;
let startDate = null;
let endDate = null;

function renderDataTable(debts){
    const tbody = document.getElementById('debt-table-body-id');
    tbody.innerHTML = '';

    if(debts.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }

    debts.forEach(debt => {
        const tableRow = document.createElement('tr');

        tableRow.classList.add('debt-row');

        tableRow.setAttribute('data-debt-id', debt.id);
        tableRow.setAttribute('data-url-associated-records', `/debts/associated/records/${debt.id}`);

        tableRow.innerHTML = `
            <th scope="row">${debt.id}</th>
            <td>${debt.person_name}</td>
            <td>${formatNumber(debt.amount)}</td>
            <td> ${formatNumber(debt.remaining_amount)} </td>
            <td>${debt.is_active ? 'ACTIVE' : 'PAID'}</td>
            <td>${debt.description}</td>
            <td>${debt.is_cash ? 'YES' : 'NO'}</td>
            <td>${debt.bank_account_nick_name}</td>
            <td>${debt.created_at}</td>
            <td>
                <div class="d-flex gap-2">
                    <button 
                        id=""
                        type="button"
                        data-bs-toggle="modal" 
                        data-bs-target="#pay-account-payable"
                        class="btn btn-outline-light" 
                        data-debt-id="${debt.id}"
                    >
                        <i class="bi bi-cash-coin"></i>
                    </button>
                    <button 
                        type="button" 
                        class="btn btn-outline-success" 
                        data-bs-toggle="modal" 
                        data-bs-target="#edit-account-payable"
                        data-debt-id="${debt.id}"
                        data-amount="${debt.amount}"
                        data-is-cash="${debt.is_cash}"
                        data-is-active="${debt.is_active}"
                        data-description="${debt.description}"
                        data-person-name="${debt.person_name}"
                        data-bank-account-id="${debt.bank_account_id}"
                    >
                        <i class="bi bi-pen"></i>
                    </button>
                    <a href="/debts/delete/${debt.id}" class="btn btn-danger"> <i class="bi bi-trash"></i></a>
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
        url = `/debts/filter/by/field?query=${filterInput.value}`;
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


        url = `/debts/filter/by/time?start=${start}&end=${end}`;
    }

    const data = await getData(url);

    renderDataTable(data.debts);

    lblTotal.textContent = 'Total: $'+ data.total;

   // startDate = null;
    // endDate = null;
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

