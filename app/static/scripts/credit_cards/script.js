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

const btnCreate = document.getElementById('btn-create-credit-card');
btnCreate.addEventListener('click', async e => createCreditCard());