export function getTotalSumOfAmounts(transactions){
    var r = 0.0;
    transactions.forEach(tran => {
        r += Number(tran.amount || 0);
    });
    return r;
}

export function formatNumber(value){
    const numberValue = Number(value || 0);
    
    return numberValue.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}