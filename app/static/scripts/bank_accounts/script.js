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

document.addEventListener('DOMContentLoaded', (event) => {
    const rows = document.querySelectorAll('.bank-row');

    rows.forEach(row => {
        row.addEventListener('click', event => {
            if(preventBtnClickWhenClickOnRow(event)) return;
            getAssociatedExpenses(row)
            .then(data => console.log(data));
        })
    });
});

