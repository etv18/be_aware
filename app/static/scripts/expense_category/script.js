function preventBtnClickWhenClickOnRow(event){
    return event.target.closest('button') || event.target.closest('form');
}

document.addEventListener('DOMContentLoaded', event => {
    const rows = document.querySelectorAll('.expense-category-row');
    rows.forEach(row => {
        row.addEventListener('dblclick', event => {
            if(preventBtnClickWhenClickOnRow(event)) return;
            let expenseCategoryId = row.getAttribute('data-expense-category-id');
            window.location.assign(`/expense_categories/associated_records/${expenseCategoryId}`)
        });
    });
});

async function createIncome(){
    const url = document.getElementById('create-endpoint-id').textContent;
    const form = document.getElementById('create-expense-category-form');
    const formData = new FormData(form);
    try {
        const response = await fetch(url, {
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
                text: data.error || 'Something went wrong while creating the income.'
            });
            return;
        }
        location.reload();//Reload the current page to see the new added income
    
    } catch (error) {
        console.error('Fetch error:', error);
        Swal.fire({
        icon: 'error',
        title: 'Network Error',
        text: error.message || 'Could not connect to server.'
        });
    }        
}

