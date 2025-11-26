function preventBtnClickWhenClickOnRow(event){
    return event.target.closest('button') || event.target.closest('form');
}

async function getAssociatedExpenses(row){
    let data;
    try {
        let bankAccountId = row.getAttribute('data-bank-account-id');
        const response = await fetch(`/bank_accounts/associated_expenses/${bankAccountId}`);
        if(!response.ok) {
            console.log(response.json())
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Something went wrong while creating the expense.'
            });
            return;
        }
        data = await response.json();
        
    } catch (error) {
        console.log(response.json())
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: data.error || 'Something went wrong while creating the expense.'
        });
    }
    return data;
}

async function associatedExpensesCreateTable(data, container){
    const table = document.createElement('table');

    //get headers dynamically from the keys (column names)
    const headers = Object.keys(data[0]);

    //---- Create thead ----
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    headers.forEach(h => {
        //Create the th element tag
        const th = document.createElement('th');

        //Add the column names from h 
        th.textContent = h.charAt(0).toUpperCase() + h.slice(1);

        //Populate the row
        headerRow.appendChild(th);
    });

    //add the populated row to the thead tag
    thead.appendChild(headerRow);

    //add the completed thead to the table
    table.appendChild(thead);

    //---- Create thead ----
    const tbody = document.createElement('tbody');

    data.forEach(item => {
        const row = document.createElement('tr')

        headers.forEach(h => {
            const td = document.createElement('td');
            td.textContent = item[h] //Get the column name
            row.appendChild(td);
        });

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

async function createBankAccount(){
    const form = document.getElementById('create-bank-account-form');
    const formData = new FormData(form);

    try {
        const response = await fetch('/bank_accounts/create', {
            method: 'POST',
            body: formData,
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });

        const data = await response.json();

        if(!response.ok){
            console.log(response.json());
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Something went wrong while creating the bank account.'
            });
            return;           
        }

        location.reload();
        
    } catch (error) {
        console.error('Fetch error: ', error);
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: error.message || 'Could not connect to server.'
        });
    }
}

async function editBankAccount(){
    const form = document.getElementById('edit-bank-account-form');
    const formData = new FormData(form);

    try {
        const response = await fetch('/bank_accounts/update', {
            method: 'PUT',
            body: formData,
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });

        const data = await response.json();

        if(!response.ok){
            console.log(response.json());
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Something went wrong while editing the bank account.'
            });
            return;           
        }

        location.reload();
        
    } catch (error) {
        console.error('Fetch error: ', error);
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: error.message || 'Could not connect to server.'
        });
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    const rows = document.querySelectorAll('.bank-row');
    const expensesTableContainer = document.getElementById('expenses-table-container');


    rows.forEach(row => {
        row.addEventListener('dblclick', async event => {
            if(preventBtnClickWhenClickOnRow(event)) return;
            let bankAccountId = row.getAttribute('data-bank-account-id');
            window.location.assign(`/bank_accounts/associated_records/${bankAccountId}`);
        });
    });
});

const btnCreateBankAccount = document.getElementById('btnSaveBankAccount');
btnCreateBankAccount.addEventListener('click',async e => createBankAccount());

const btnEditBankAccount = document.getElementById('btn-edit-bank-account');
btnEditBankAccount.addEventListener('click', async e => editBankAccount());