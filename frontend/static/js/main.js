document.addEventListener('DOMContentLoaded', function() {
    const workflowForm = document.getElementById('workflowForm');
    const workflowList = document.getElementById('workflowList');

    // Get the backend URL from the window location
    const backendUrl = window.location.origin;
    console.log('Backend URL:', backendUrl); // Debug log

    workflowForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            propertyName: document.getElementById('propertyName').value,
            leaseEndDate: document.getElementById('leaseEndDate').value,
            exitReason: document.getElementById('exitReason').value
        };

        try {
            console.log('Sending request to:', `${backendUrl}/api/workflow/lease-exit/create`); // Debug log
            const response = await fetch(`${backendUrl}/api/workflow/lease-exit/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const result = await response.json();
                showAlert('success', 'Workflow created successfully!');
                workflowForm.reset();
                addWorkflowToList(result.workflow_id, formData);
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create workflow');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('danger', error.message || 'Failed to create workflow. Please try again.');
        }
    });

    function addWorkflowToList(workflowId, formData) {
        const listItem = document.createElement('a');
        listItem.href = '#';
        listItem.className = 'list-group-item list-group-item-action';
        listItem.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">${formData.propertyName}</h5>
                <small>ID: ${workflowId}</small>
            </div>
            <p class="mb-1">End Date: ${formData.leaseEndDate}</p>
            <small class="text-muted">Reason: ${formData.exitReason}</small>
        `;
        workflowList.prepend(listItem);
    }

    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        workflowForm.parentElement.insertBefore(alertDiv, workflowForm);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});