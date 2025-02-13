document.addEventListener('DOMContentLoaded', function() {
    const workflowForm = document.getElementById('workflowForm');
    const workflowList = document.getElementById('workflowList');

    // Get the backend URL from the environment
    const backendUrl = window.location.protocol + '//' + window.location.host;
    console.log('Backend URL:', backendUrl); // Debug log

    workflowForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Show loading state
        const submitButton = this.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Creating...';

        const formData = {
            propertyName: document.getElementById('propertyName').value,
            leaseEndDate: document.getElementById('leaseEndDate').value,
            exitReason: document.getElementById('exitReason').value,
            createdAt: new Date().toISOString()
        };

        try {
            console.log('Sending request to:', `${backendUrl}/api/workflow/lease-exit/create`); // Debug log
            const response = await fetch(`${backendUrl}/api/workflow/lease-exit/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            showAlert('success', 'Workflow created successfully!');
            workflowForm.reset();
            addWorkflowToList(result.workflow_id, formData);

        } catch (error) {
            console.error('Error:', error);
            showAlert('danger', `Failed to create workflow: ${error.message}`);
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });

    function addWorkflowToList(workflowId, formData) {
        const listItem = document.createElement('a');
        listItem.href = '#';
        listItem.className = 'list-group-item list-group-item-action';
        listItem.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">${formData.propertyName}</h5>
                <small>Created: ${new Date().toLocaleDateString()}</small>
            </div>
            <p class="mb-1">End Date: ${formData.leaseEndDate}</p>
            <small class="text-muted">Reason: ${formData.exitReason}</small>
        `;

        // Add to the beginning of the list
        if (workflowList.firstChild) {
            workflowList.insertBefore(listItem, workflowList.firstChild);
        } else {
            workflowList.appendChild(listItem);
        }

        // Show success message
        showAlert('success', `Workflow ${workflowId} created successfully`);
    }

    function showAlert(type, message) {
        // Remove any existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Insert before the form
        const cardBody = workflowForm.closest('.card-body');
        cardBody.insertBefore(alertDiv, cardBody.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});