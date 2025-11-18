import {renderExpensesTable} from './filteringByTime.js';

const link = document.getElementById('filter-by-cash');
const limit = document.getElementById('weekly-limit');
const title = document.getElementById('weekly-title');
const spent = document.getElementById('weekly-spent');
const left = document.getElementById('weekly-left');

async function getData(){
    const is_cash = link.getAttribute('data-is-cash-value') === 'True' ? 1 : 0;
    let response;
    let data;

    try {
        response = await fetch(`/expenses/filter_expenses_by_cash/${is_cash}`);
        if(!response.ok){
            console.log(response.json());
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Something went wrong'
            });
            return;
        }
        data = await response.json();
        console.log(data);
    } catch (error) {
        console.error(error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: data.error || 'Something went wrong'
        });
    }

    return data;
}

link.addEventListener('click', async () => {
    const data = await getData();
    renderExpensesTable(data.expenses);
    title.textContent = `DATA`;
    limit.textContent = `Count: ${data.count}`;
    spent.textContent = `Total: ${data.total}`;
    left.textContent = '';
});