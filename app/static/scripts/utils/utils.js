document.addEventListener('click', async e => {
    const btn = e.target.closest('a.btn-danger');
    if(!btn) return;

    e.preventDefault();

    const deleteUrl = btn.getAttribute('href');

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
            const res = await fetch(deleteUrl, {
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

