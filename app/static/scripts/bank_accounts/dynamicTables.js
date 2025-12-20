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

const colSpan = {
    expenses: 7,
    incomes: 6,
    withdrawals: 5,
    loans: 9,
    loanPayments: 5,
    creditCardPayments: 5
}

const tdHtmlExpenses = (expense) => `
    <th scope="row">${expense.id}</th>
    <td>${expense.amount}</td>
    <td>${expense.is_cash ? 'YES' : 'NO'}</td>
    <td>${expense.description ?? '-'}</td>
    <td>${expense.credit_card_name ?? '-'}</td>
    <td>${expense.bank_account_name ?? '-'}</td>
    <td>${expense.expense_category_name ?? '-'}</td>
    <td>${expense.created_at}</td>
`;

const tdHtmlIncomes = (income) => `
    <th scope="row">${ income.id }</th>
    <td>${ income.amount }</td>
    <td>${ income.is_cash ? 'YES' : 'NO'}</td>
    <td>${ income.description ?? '-' }</td>
    <td>${ income.bank_nick_name ?? '-'}</td>
    <td>${ income.created_at }</td>
`;

const tdHtmlWithdrawals = (withdrawal) => `
    <th scope="row">${ withdrawal.id }</th>
    <td>${ withdrawal.amount }</td>
    <td>${ withdrawal.description ?? '-'}</td>
    <td>${ withdrawal.bank_account_nick_name ?? '-' }</td>
    <td>${ withdrawal.created_at }</td>
`;

const tdHtmlLoans = (loan) => `
    <th scope="row">${loan.id}</th>
    <td>${loan.person_name ?? '-'}</td>
    <td>${loan.amount}</td>
    <td> ${loan.remaining_amount} </td>
    <td>${loan.is_active ? 'ACTIVE' : 'PAID'}</td>
    <td>${loan.description ?? '-'}</td>
    <td>${loan.is_cash ? 'YES' : 'NO'}</td>
    <td>${loan.bank_account_nick_name ?? '-'}</td>
    <td>${loan.created_at}</td>
`;

const tdHtmlLoanPayments = (loanPayment) => `
    <th scope="row">${ loanPayment.id }</th>
    <td class="text-start">${ loanPayment.amount }</td>
    <td>${ loanPayment.is_cash ? 'YES' : 'NO' }</td>
    <td>${ loanPayment.bank_account_nick_name ?? '-'}</td>
    <td>${ loanPayment.created_at }</td>
`;

const tdHtmlCreditCardPayments = (creditCardPayment) => `
    <th scope="row">${ creditCardPayment.id }</th>
    <td class="text-start">${ creditCardPayment.amount }</td>
    <td>${ creditCardPayment.credit_card_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.bank_account_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.created_at }</td>
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

function renderDataTable(objList, tbody, templateFunction, colspanValue){
    tbody.innerHTML = '';

    if(!objList || objList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="${colspanValue}" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }

    objList.forEach(obj => {
        const tableRow = document.createElement('tr');
        tableRow.innerHTML = templateFunction(obj);
        tbody.appendChild(tableRow)
    });
}

function filterTableData(dataSet, query, fields){
    if(query === null || query === undefined || query === '') {
        return dataSet;
    }

    var term = query.toLowerCase(); //User input

    var filteredList = [];

    dataSet.forEach(item => {
        var itemMatches = false;

        for(var i = 0; i < fields.length; i++){
            var key = fields[i];
            var value = item[key]; //Looking in the js object

            if(value === null || value === undefined){
                continue;
            }

            var valueAsString = String(value).toLowerCase(); //Value of the data set

            if(valueAsString.indexOf(term) !== -1){
                itemMatches = true;
                break;
            }
        }
        if(itemMatches) filteredList.push(item);
    });

    return filteredList;
}
