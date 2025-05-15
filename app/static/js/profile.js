/********************************
 * FAMILY MANAGEMENT CONTROLLER *
 ********************************/
console.log("Family Manager JS loaded!");

/*********************
 * API COMMUNICATION *
 *********************/
const API_BASE = '/api/family'; // Base endpoint for family operations

// Retrieve CSRF token from the form
function getCSRFToken() {
    return document.querySelector('input[name="csrf_token"]')?.value || '';
}

/**
 * Deletes a family member from the server
 * @param {string} memberId - ID of member to delete
 * @returns {Promise<Object>} Server response
 */
async function deleteMember(memberId) {
    try {
        const response = await fetch(`${API_BASE}/${memberId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        return await response.json();
    } catch (error) {
        console.error('Delete failed:', error);
        return { success: false, error: 'Network error' };
    }
}

/**
 * Adds a new family member to the server
 * @param {Object} memberData - {first_name, last_name, email}
 * @returns {Promise<Object>} Server response with new member data
 */
async function addMember(memberData) {
    try {
        const response = await fetch(API_BASE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(memberData)
        });
        return await response.json();
    } catch (error) {
        console.error('Add failed:', error);
        return { success: false, error: 'Network error' };
    }
}

/********************
 * UI COMPONENTS *
 ********************/

/**
 * Shows a temporary notification toast
 * @param {string} message - Text to display
 * @param {string} type - success/error/warning/info
 */
function showToast(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg transform translate-y-10 opacity-0 transition-all duration-300`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-10', 'opacity-0');
        toast.classList.add('translate-y-0', 'opacity-100');
    }, 10);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-10');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Creates a new family member card element
 * @param {Object} member - Member data from server
 * @returns {HTMLElement} Configured member card
 */
function createMemberCard(member) {
    const initials = `${member.first_name.charAt(0)}${member.last_name.charAt(0)}`.toUpperCase();
    const newMember = document.createElement('div');
    newMember.className = 'family-member relative bg-gray-50 p-4 rounded-xl flex items-center justify-between cursor-move';
    newMember.setAttribute('draggable', 'true');
    newMember.dataset.id = member.id;
    
    newMember.innerHTML = `
        <div class="flex items-center space-x-4">
            <div class="w-12 h-12 rounded-full bg-gray-300 flex items-center justify-center text-gray-600">
                <span class="text-lg font-medium">${initials}</span>
            </div>
            <div>
                <h3 class="font-medium text-gray-800">${member.first_name} ${member.last_name}</h3>
                <p class="text-sm text-gray-500">${member.role || 'Member'}</p>
                ${member.email ? `<p class="text-xs text-gray-400">${member.email}</p>` : ''}
            </div>
        </div>
        <div class="flex space-x-2">
            <button class="edit-member p-2 text-gray-500 hover:text-gray-700">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
            </button>
        </div>
    `;
    
    setupDragEvents(newMember);
    setupEditButton(newMember.querySelector('.edit-member'));
    return newMember;
}

/********************
 * EVENT HANDLERS *
 ********************/

/**
 * Sets up drag events for a member card
 * @param {HTMLElement} member - Member card element
 */
function setupDragEvents(member) {
    member.addEventListener('dragstart', function() {
        draggedMember = this;
        setTimeout(() => {
            this.classList.add('dragging');
        }, 0);
        deleteZone.classList.remove('hidden');
    });
    
    member.addEventListener('dragend', function() {
        this.classList.remove('dragging');
        deleteZone.classList.add('hidden');
        deleteZone.classList.remove('active');
    });
}

/**
 * Sets up edit functionality for a member card
 * @param {HTMLElement} button - Edit button element
 */
function setupEditButton(button) {
    button.addEventListener('click', function() {
        const memberCard = this.closest('.family-member');
        const name = memberCard.querySelector('h3').textContent;
        const email = memberCard.querySelector('p.text-xs')?.textContent || '';
        
        // Create inline edit form
        const form = document.createElement('form');
        form.className = 'p-4 bg-white rounded-lg shadow-xl absolute top-0 left-0 w-full z-10';
        form.innerHTML = `
            <h4 class="font-bold mb-3">Edit Member</h4>
            <div class="space-y-3">
                <input type="text" value="${name}" class="w-full px-3 py-2 border rounded">
                <input type="email" value="${email}" class="w-full px-3 py-2 border rounded" placeholder="Email">
            </div>
            <div class="flex justify-end space-x-2 mt-4">
                <button type="button" class="cancel-edit px-3 py-1 text-gray-600">Cancel</button>
                <button type="submit" class="px-3 py-1 bg-blue-500 text-white rounded">Save</button>
            </div>
        `;
        
        memberCard.appendChild(form);
        
        // Cancel button handler
        form.querySelector('.cancel-edit').addEventListener('click', () => form.remove());
        
        // Submit handler
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            // TODO: Implement update functionality
            form.remove();
        });
    });
}

/********************
 * INITIALIZATION *
 ********************/
document.addEventListener('DOMContentLoaded', () => {
    console.log("Family Manager initialized");
    console.log("DOM ready - family buttons should work now");

    // DOM Elements
    const addButton = document.getElementById('add-family-member');
    const newMemberForm = document.getElementById('new-member-form');
    const cancelButton = document.getElementById('cancel-add-member');
    const membersContainer = document.getElementById('family-members-container');
    const deleteZone = document.getElementById('delete-zone');
    const addMemberForm = document.getElementById('add-member-form');
    let draggedMember = null;

    /**
     * Loads family members from server
     */
    async function loadFamilyMembers() {
        try {
            const response = await fetch(API_BASE);
            const data = await response.json();
            
            membersContainer.innerHTML = '';
            data.members.forEach(member => {
                membersContainer.appendChild(createMemberCard(member));
            });
        } catch (error) {
            console.error('Failed to load members:', error);
            showToast('Failed to load family members', 'error');
        }
    }

    // Event: Toggle Add Member Form
    addButton.addEventListener('click', () => {
        newMemberForm.classList.toggle('hidden');
    });

    // Event: Cancel Add Member
    cancelButton.addEventListener('click', () => {
        newMemberForm.classList.add('hidden');
    });

    // Drag and Drop Handlers
    deleteZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('active');
    });

    deleteZone.addEventListener('dragleave', function() {
        this.classList.remove('active');
    });

    // Event: Delete Member on Drop
    deleteZone.addEventListener('drop', async function(e) {
        e.preventDefault();
        if (!draggedMember) return;
        
        const memberId = draggedMember.dataset.id;
        if (!confirm(`Remove ${draggedMember.querySelector('h3').textContent}?`)) {
            this.classList.remove('active', 'hidden');
            return;
        }

        draggedMember.classList.add('opacity-50', 'pointer-events-none');
        const result = await deleteMember(memberId);
        
        if (result.success) {
            draggedMember.remove();
            showToast('Member removed', 'success');
        } else {
            showToast(result.error || 'Failed to remove', 'error');
            draggedMember.classList.remove('opacity-50', 'pointer-events-none');
        }
        
        this.classList.remove('active', 'hidden');
    });

    // Event: Add New Member Form Submission
    addMemberForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            first_name: this.querySelector('input[type="text"]:nth-of-type(1)').value.trim(),
            last_name: this.querySelector('input[type="text"]:nth-of-type(2)').value.trim(),
            email: this.querySelector('input[type="email"]').value.trim()
        };

        if (!formData.first_name) {
            showToast('First name is required', 'warning');
            return;
        }

        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Adding...';

        const result = await addMember(formData);
        
        if (result.success) {
            membersContainer.appendChild(createMemberCard(result.member));
            this.reset();
            newMemberForm.classList.add('hidden');
            showToast('Member added', 'success');
        } else {
            showToast(result.error || 'Failed to add member', 'error');
        }

        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Add Member';
    });

    // Initial Data Load
    loadFamilyMembers();

    // Profile Picture Upload Handler
    const profilePicBtn = document.querySelector('.relative button');
    if (profilePicBtn) {
        profilePicBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*';
            fileInput.click();
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files[0]) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        const img = document.querySelector('.rounded-full.border-4');
                        if (img) img.src = event.target.result;
                    };
                    reader.readAsDataURL(e.target.files[0]);
                }
            });
        });
    }

    // Navbar Profile Button (if not using data-page-redirect)
    document.querySelector('nav a[href="/profile"]')?.addEventListener('click', (e) => {
        if (!e.target.closest('[data-page-redirect]')) {
            e.preventDefault();
            window.location.href = '/profile';
        }
    });
});