const tBodyExpense = document.getElementById('expenses-table-body');
const tBodyIncome = document.getElementById('incomes-table-body');
const tBodyWithdrawal = document.getElementById('withdrawals-table-body');
const tBodyLoan = document.getElementById('loans-table-body');
const tBodyLoanPayment = document.getElementById('loan-payment-table-body');
const tBodyCreditCard = document.getElementById('credit-card-payment-table-body');

let expenses;
let incomes;
let withdrawals;
let loans;
let loanPayments;
let creditCardPayments;


const tdHtmlExpenses = `
    <th scope="row">${expense.id}</th>
    <td>${expense.amount}</td>
    <td>${expense.is_cash ? 'Yes' : 'No'}</td>
    <td>${expense.description || '-'}</td>
    <td>${expense.credit_card_name || '-'}</td>
    <td>${expense.bank_account_name || '-'}</td>
    <td>${expense.expense_category_name || '-'}</td>
    <td>${expense.created_at}</td>
`;

const tdHtmlIncomes = `
    <th scope="row">${ income.id }</th>
    <td>${ income.amount }</td>
    <td>${ income.is_cash }</td>
    <td>${ income.description ? income.description : '-' }</td>
    <td>${ income.bank_nick_name }</td>
    <td>${ income.created_at }</td>
`;

const tdHtmlWithdrawals = `
    <th scope="row">${ withdrawal.id }</th>
    <td>${ withdrawal.amount }</td>
    <td>${ withdrawal.description ? withdrawal.description : '-'}</td>
    <td>${ withdrawal.bank_account_nick_name }</td>
    <td>${ withdrawal.created_at }</td>
`;

const tdHtmlLoans = `
    <th scope="row">${loan.id}</th>
    <td>${loan.person_name}</td>
    <td>${loan.amount}</td>
    <td> ${loan.remaining_amount} </td>
    <td>${loan.is_active ? 'ACTIVE' : 'PAID'}</td>
    <td>${loan.description}</td>
    <td>${loan.is_cash ? 'YES' : 'NO'}</td>
    <td>${loan.bank_account_nick_name}</td>
    <td>${loan.created_at}</td>
`;

const tdHtmlLoanPayments = `

`;

const tdHtmlCreditCardPayments = `
    <th scope="row">${ creditCardPayments.id }</th>
    <td class="text-start">${ creditCardPayments.amount }</td>
    <td>${ creditCardPayments.credit_card_nick_name }</td>
    <td>${ creditCardPayments.bank_nick_name }</td>
    <td>${ creditCardPayments.created_at }</td>
`;

async function getData(url){
    let data;

    try {
        const response = await fetch(url);
        if(!response.ok) {
            console.log(response.json());
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Something went wrong while creating the expense.'
            });
            return;
        }
        data = await response.json();
        console.log(data);
        
        expenses = data?.expenses ?? [];
        incomes = data?.incomes ?? [];
        withdrawals = data?.withdrawals ?? [];
        loans = data?.loans ?? [];
        loanPayments = data?.loanPayments ?? [];
        creditCardPayments = data?.creditCardPayments ?? [];
        
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: error.message || 'Could not connect to server.'
        });
    }
}

function renderDataTable(objList, htmlTableData){

}


