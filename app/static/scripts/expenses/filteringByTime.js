let startDate;
let endDate;

const timeRange = flatpickr('#start-date-id', {
    mode: 'range',
    altInput: true,
    altFormat: 'M j, Y',
    dateFormat: 'Y-m-d',
    onChange: (selectedDates, dateStr, instance) => {
        if(selectedDates.length === 2){
            startDate = selectedDates[0];
            endDate = selectedDates[1];
        }
    },
});

async function getDataFilteredByTime(){
    const start = timeRange.formatDate(startDate, 'Y-m-d');
    const end = timeRange.formatDate(endDate, 'Y-m-d');

    try {
        const response = await fetch(`/expenses/filter_by_time?start=${start}&end=${end}`);
        if(!response.ok) {
            console.log(response.json());
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Something went wrong while creating the expense.'
            });
            return;
        }
        const data = await response.json();
        console.log(data);
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: err.message || 'Could not connect to server.'
        });
    }
}

/*
best way to compare to undifined values, it only matches expecifically undefined values
if (typeof yourVariable === 'undefined') {...}
*/


