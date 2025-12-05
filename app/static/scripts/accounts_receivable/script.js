function preventBtnClickWhenClickOnRow(event){
    return event.target.closest('button') || event.target.closest('form');
}

document.addEventListener('DOMContentLoaded', (event) => {
    const rows = document.querySelectorAll('.loan-row');
    rows.forEach(row => {
        row.addEventListener('dblclick', e => {
            if(preventBtnClickWhenClickOnRow(e)) return;
            const loanId = row.getAttribute('data-loan-id');
            const url = row.getAttribute('data-url-associated-records');
            window.location.href = url;
        });
    });
});
