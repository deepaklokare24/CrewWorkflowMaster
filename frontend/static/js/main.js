document.addEventListener('DOMContentLoaded', function() {
    const workflowForm = document.getElementById('workflowForm');
    const workflowList = document.getElementById('workflowList');

    workflowForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            propertyName: document.getElementById('propertyName').value,
            leaseEndDate: document.getElementById('leaseEndDate').value,
            exitReason: document.getElementById('exitReason').value
        };

        try {
            const response = await fetch('http://localhost:8000/api/workflow/lease-exit/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const result = await response.json();
                alert('Workflow created successfully!');
                workflowForm.reset();
                addWorkflowToList(result.workflow_id, formData);
            } else {
                throw new Error('Failed to create workflow');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create workflow. Please try again.');
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
        `;
        workflowList.prepend(listItem);
    }
});
