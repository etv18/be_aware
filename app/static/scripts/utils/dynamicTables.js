
export {
    expensesTemplateFn,
    incomesTemplateFn,
    withdrawalsTemplateFn,
    loansTemplateFn,
    loanPaymentsTemplateFn,
    creditCardPaymentsTemplateFn,
    renderDataTable,
    filterTableData,
    colSpan,
    getKeysFromDataSet
};

const expensesTemplateFn = (expense) => `
    <th scope="row">${expense.id}</th>
    <td class="text-start">${formatNumber(expense.amount)}</td>
    <td>${expense.is_cash ? 'YES' : 'NO'}</td>
    <td class="text-start">${expense.description ?? '-'}</td>
    <td>${expense.credit_card_name ?? '-'}</td>
    <td>${expense.bank_account_name ?? '-'}</td>
    <td class="text-start">${expense.expense_category_name ?? '-'}</td>
    <td>${expense.created_at}</td>
`;

const incomesTemplateFn = (income) => `
    <th scope="row">${ income.id }</th>
    <td class="text-start">${ formatNumber(income.amount) }</td>
    <td>${ income.is_cash ? 'YES' : 'NO'}</td>
    <td class="text-start">${ income.description ?? '-' }</td>
    <td>${ income.bank_nick_name ?? '-'}</td>
    <td>${ income.created_at }</td>
`;

const withdrawalsTemplateFn = (withdrawal) => `
    <th scope="row">${ withdrawal.id }</th>
    <td>${ formatNumber(withdrawal.amount) }</td>
    <td>${ withdrawal.description ?? '-'}</td>
    <td>${ withdrawal.bank_account_nick_name ?? '-' }</td>
    <td>${ withdrawal.created_at }</td>
`;

const loansTemplateFn = (loan) => `
    <th scope="row">${loan.id}</th>
    <td class="text-start">${loan.amount}</td>
    <td>${loan.is_cash ? 'YES' : 'NO'}</td>
    <td>${loan.person_name ?? '-'}</td>
    <td> ${loan.remaining_amount} </td>
    <td>${loan.is_active ? 'ACTIVE' : 'PAID'}</td>
    <td class="text-start">${loan.description ?? '-'}</td>
    <td>${loan.bank_account_nick_name ?? '-'}</td>
    <td>${loan.created_at}</td>
`;

const loanPaymentsTemplateFn = (loanPayment) => `
    <th scope="row">${ loanPayment.id }</th>
    <td class="text-start">${ loanPayment.amount }</td>
    <td>${ loanPayment.is_cash ? 'YES' : 'NO' }</td>
    <td>${ loanPayment.bank_account_nick_name ?? '-'}</td>
    <td>${ loanPayment.created_at }</td>
`;

const creditCardPaymentsTemplateFn = (creditCardPayment) => `
    <th scope="row">${ creditCardPayment.id }</th>
    <td class="text-start">${ creditCardPayment.amount }</td>
    <td>${ creditCardPayment.credit_card_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.bank_account_nick_name ?? '-' }</td>
    <td>${ creditCardPayment.created_at }</td>
`;

const colSpan = {
    EXPENSES: 7,
    INCOMES: 6,
    WITHDRAWALS: 5,
    LOANS: 9,
    LOAN_PAYMENTS: 5,
    CREDIT_CARD_PAYMENTS: 5
}

function renderDataTable(objList, tbody, templateFunction, colspanValue){
    tbody.innerHTML = '';

    if(!objList || objList.length === 0 || objList === undefined) {
        tbody.innerHTML = `
            <tr>
                <td colspan="${colspanValue}" class="text-center text-muted">No results found.</td>
            </tr>  
        `;
        return;
    }
    console.log( `${objList}`);
    objList.forEach(obj => {
        const tableRow = document.createElement('tr');
        tableRow.innerHTML = templateFunction(obj);
        tbody.appendChild(tableRow)
    });
}


function filterTableData(dataSet, query){
    if(query === null || query === undefined || query === '') {
        return dataSet;
    }

    var fields = getKeysFromDataSet(dataSet);

    if(fields.length === 0) return dataSet;

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

function getKeysFromDataSet(dataSet){
    if(!Array.isArray(dataSet) || dataSet.length === 0){
        return [];
    }
    console.log('===> MMMMMMM $',JSON.parse(JSON.stringify(dataSet)));
    return Object.keys(dataSet[0]);
}