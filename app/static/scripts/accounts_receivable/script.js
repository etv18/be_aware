function preventBtnClickWhenClickOnRow(event){
    return event.target.closest('button') || event.target.closest('form');
}

document.addEventListener('DOMContentLoaded', (event) => {
    const tbody = document.getElementById('loans-table-body-id');
   
    //This block of code allows me to make the dblclick event even though
    //when the content of the table is re-render dynamically with js in the
    //frontend
    tbody.addEventListener('dblclick', e => {
        if(preventBtnClickWhenClickOnRow(e)) return;
        
        const row = e.target.closest('.loan-row');
        if (!row) return; 
        
        const url = row.getAttribute('data-url-associated-records');
        window.location.href = url;
    });
 
});
