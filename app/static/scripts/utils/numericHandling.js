function getTotalSumOfAmounts(transactions){
    var r = 0.0;
    transactions.forEach(tran => {
        r += Number(tran.amount || 0);
    });
    return r;
}

function formatNumber(value){
    const numberValue = Number(value || 0);
    return numberValue.toLocaleString('en-US');
}