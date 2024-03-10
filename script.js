document.addEventListener('DOMContentLoaded', function() {
    setupDropArea('ordersDropArea', 'ordersInput', 'ordersList', 'orders');
    setupDropArea('trackingDropArea', 'trackingInput', 'trackingList', 'tracking');

    document.getElementById('confirmUpload').addEventListener('click', function() {
        window.location.href = '/confirm';
    });

    setupColumnToggle();
});

function setupDropArea(dropAreaId, inputId, listId, category) {
    let dropArea = document.getElementById(dropAreaId);
    let input = document.getElementById(inputId);

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    dropArea.addEventListener('drop', (e) => handleDrop(e, input, listId, category));
    dropArea.addEventListener('click', () => input.click());
    input.addEventListener('change', () => handleFiles(input.files, listId, category));
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e, input, listId, category) {
    let dt = e.dataTransfer;
    let files = dt.files;

    // Append files from drop to input for a consistent upload handling
    input.files = files;
    handleFiles(files, listId, category);
}

function handleFiles(files, listId, category) {
    // Create FormData outside the loop to append multiple files
    let formData = new FormData();
    formData.append('category', category); // Append category once
    
    [...files].forEach(file => {
        formData.append('files[]', file); // Use 'files[]' to denote it's an array of files
        displayUploadedFile(file, listId); // Function to display uploaded file name in the list
    });

    // Make a single POST request with all files in the category
    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        console.log('Upload successful:', data);
    })
    .catch(error => console.error('Upload error:', error));
}

function displayUploadedFile(file, listId) {
    let list = document.getElementById(listId);
    let item = document.createElement('li');
    item.textContent = file.name; // Display the file name
    list.appendChild(item);
}

function setupColumnToggle() {
    document.querySelectorAll('.column-toggle').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const columnIndex = checkbox.dataset.column;
            const displayStyle = checkbox.checked ? '' : 'none';
            document.querySelectorAll(`.table td:nth-child(${parseInt(columnIndex) + 1}), .table th:nth-child(${parseInt(columnIndex) + 1})`).forEach(cell => {
                cell.style.display = displayStyle;
            });
        });
    });
}
