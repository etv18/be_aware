const amountInput = document.getElementById('t-amount-id');
const transferIdInput = document.getElementById('transfer-id');
const selectBankAccount = document.getElementById('to-bank-account-select-id');
const editTransferModal = document.getElementById('edit-bank-transfer');
const btnUpdateTransfer = document.getElementById('btn-edit-bank-transfer');
let updateEndpoint = null;


async function updateBankTransfer(){
    const form = document.getElementById('edit-bank-transfer-form');
    const formData = new FormData(form);
    try {
        const response = await fetch(updateEndpoint, {
            method: 'PUT',
            body: formData,
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

editTransferModal.addEventListener('show.bs.modal', e => {
    const btn = e.relatedTarget;
    const oldAmount = btn.getAttribute('data-amount');
    const transferId = btn.getAttribute('data-transfer-id');
    const toBankAccountId = btn.getAttribute('data-to-bank-account-id');
    updateEndpoint = btn.getAttribute('data-update-endpoint');
    
    amountInput.value = oldAmount;
    selectBankAccount.value = toBankAccountId;
    transferIdInput.value = transferId;
});

btnUpdateTransfer.addEventListener('click', async e => {
    await updateBankTransfer();
});