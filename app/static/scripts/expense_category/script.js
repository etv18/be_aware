function preventBtnClickWhenClickOnRow(event){
    return event.target.closest('button') || event.target.closest('form');
}

document.addEventListener('DOMContentLoaded', event => {
    const rows = document.querySelectorAll('.expense-category-row');
    rows.forEach(row => {
        row.addEventListener('click', event => {
            if(preventBtnClickWhenClickOnRow(event)) return;
            let expenseCategoryId = row.getAttribute('data-expense-category-id');
            window.location.assign(`/expense_categories/associated_records/${expenseCategoryId}`)
        });
    });
});