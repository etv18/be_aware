const endpoint = document.getElementById('total-monthly-per-associated-record-info-endpoint-id').value;

const expensesTotal = document.getElementById('monthly-expenses-total-id');
const incomesTotal = document.getElementById('monthly-incomes-total-id');
const loanPaymentTotal = document.getElementById('monthly-loan-payment-total-id');
const loansTotal = document.getElementById('monthly-loans-total-id');
const creditCardPaymentsTotal = document.getElementById('monthly-credit-card-payments-total-id');
const transfersOutgoingsTotal = document.getElementById('monthly-transfers-outgoings-total-id');
const transfersIncomingsTotal = document.getElementById('monthly-transfers-incomings-total-id');
const withdrawalsTotal = document.getElementById('monthly-withdrawals-total-id');
const depositsTotal = document.getElementById('monthly-deposits-total-id');
const debtsTotal = document.getElementById('monthly-debts-total-id');
const debtsPaymentsTotal = document.getElementById('monthly-debt-payments-total-id');

async function getMonthlyTotalPerAssociatedRecord(){
    try {
        response = await fetch(endpoint);
        if(!response.ok) {
            console.log(response.json());
            return;
        }

        const data = await response.json();
        
        return data;
    } catch (error) {
        console.error(error);
        throw new Error();
    }
}

function formatNumber(value){
    const numberValue = Number(value || 0);
    
    return '$'+numberValue.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

document.addEventListener('DOMContentLoaded', async e => {
    const data = await getMonthlyTotalPerAssociatedRecord();

    expensesTotal.textContent = formatNumber(data.monthly_totals.expenses);
    incomesTotal.textContent = formatNumber(data.monthly_totals.incomes);
    loanPaymentTotal.textContent = formatNumber(data.monthly_totals.loan_payment);
    loansTotal.textContent = formatNumber(data.monthly_totals.loans);
    creditCardPaymentsTotal.textContent = formatNumber(data.monthly_totals.credit_card_payments);
    transfersOutgoingsTotal.textContent = formatNumber(data.monthly_totals.transfers_outgoings);
    transfersIncomingsTotal.textContent = formatNumber(data.monthly_totals.transfers_incomings);
    withdrawalsTotal.textContent = formatNumber(data.monthly_totals.withdrawals);
    depositsTotal.textContent = formatNumber(data.monthly_totals.deposits);
    debtsTotal.textContent = formatNumber(data.monthly_totals.debts);
    debtsPaymentsTotal.textContent = formatNumber(data.monthly_totals.debt_payments);
});