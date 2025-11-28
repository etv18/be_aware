const btnDeleteList = document.querySelectorAll('a.btn-danger');

btnDeleteList.forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.preventDefault(); // stop the default action
        
        const deleteUrl = btn.getAttribute('href');
        console.log(deleteUrl)
        Swal.fire({
            title: "Are you sure?",
            text: "This record will be deleted.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Yes, delete it!"
        }).then(async (result) => {
            if (result.isConfirmed) {

                res = await fetch(`${deleteUrl}`, {
                    method: 'DELETE'
                });
                console.log(res.json());
                
                if (res.ok) {
                    location.reload();
                } else {
                    Swal.fire("Error", "Could not delete record", "error");
                }
            }
        });
    });
});

