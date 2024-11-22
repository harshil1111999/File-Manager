const deleteButton = document.getElementById('deleteButton');
const confirmDeleteButton = document.getElementById('confirmDelete');
const loader = document.getElementById("loader");
const resultsContainer = document.getElementById("results-container");
let deleteDocId;

function setDeleteDocument(doc_id) {
    deleteDocId = doc_id;
}

function submitForm() {
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);

    const button = document.getElementById('uploadDocument');
    const spinner = button.querySelector('.spinner-border');
    const buttonText = button.querySelector('.button-text');

    // Show spinner and disable button
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Processing...';
    button.disabled = true;

    // Use fetch API to submit the form data to the server
    fetch('/upload_file', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.message || "Unknown error occurred");
            });
        }

        // Display the server response message
        const uploadToast = new bootstrap.Toast(document.getElementById('uploadToast'));
        uploadToast.show();

        // Clear the form
        form.reset();
    }).catch(error => {
        console.error('Error:', error);
    }).finally(() => {
        // Hide spinner and re-enable button after API call
        spinner.classList.add('d-none');
        buttonText.textContent = 'Upload Document';
        button.disabled = false;
    });
}

function closeModal() {
    // Close the modal
    const modalElement = document.getElementById('deleteModal');
    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
    modalInstance.hide();

    // Remove the backdrop manually
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
}

function showLoader() {
    // Show the loader
    document.getElementById("loader").classList.remove("d-none");
}

document.getElementById('clearButton').addEventListener('click', function () {
    const searchInput = document.getElementById('query');
    searchInput.value = ''; // Clear the input field
    searchInput.focus();    // Bring focus back to the input
});

confirmDeleteButton.addEventListener('click', function () {
    if (deleteDocId) {
        // Example DELETE API call
        fetch(`/document/${deleteDocId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(data => {
                closeModal();
                console.log('Delete successful:', data);
                alert(`Document "${deleteDocId}" deleted successfully!`);
            })
            .catch(error => {
                closeModal();
                console.error('Error during delete:', error);
                alert('Failed to delete the document.');
            });
    } else {
        alert('No document specified for deletion.');
    }

});