async function getDataByCategory(){
    let data;
    try {
        const response = await fetch(`/expense_categories/monthly/chart`)
    } catch (error) {
        console.error(error);
    }

    return data;
}