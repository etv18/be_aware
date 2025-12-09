async function createCreditCard(){
    const form = document.getElementById('create-credit-card-form');
    const formData = new FormData(form);

    try {
        const response = await fetch('/credit_cards/create', {
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
                text: data.error || 'Something went wrong while creating the credit cards.'
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

async function editCreditCard(){
    const form = document.getElementById('edit-credit-card-form');
    const formData = new FormData(form);

    try {
        const response = await fetch('/credit_cards/update', {
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
                text: data.error || 'Something went wrong while editing the credit cards.'
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

function preventBtnClickWhenClickOnRow(event){
    return event.target.closest('button') || event.target.closest('form');
}

document.addEventListener('DOMContentLoaded', e => {
    const rows = document.querySelectorAll('.credit-card-rows');
    rows.forEach(row => {
        row.addEventListener('dblclick', e => {
            if(preventBtnClickWhenClickOnRow(e)) return;
            let url = row.getAttribute('data-url-associated-records');
            window.location.assign(url);
        });
    }); 
});

const btnCreateCreditCard = document.getElementById('btn-create-credit-card');
btnCreateCreditCard.addEventListener('click', async e => createCreditCard());

const btnEditCreditCard = document.getElementById('btn-edit-credit-card');
btnEditCreditCard.addEventListener('click', async e => editCreditCard());