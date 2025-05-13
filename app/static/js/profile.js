console.log("Family Manager JS loaded!");
document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM ready - family buttons should work now");
});


document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-family-member');
    const newMemberForm = document.getElementById('new-member-form');
    const cancelButton = document.getElementById('cancel-add-member');
    const membersContainer = document.getElementById('family-members-container');
    const deleteZone = document.getElementById('delete-zone');
    const addMemberForm = document.getElementById('add-member-form');
    
    // Toggle add member form
    addButton.addEventListener('click', () => {
        newMemberForm.classList.toggle('hidden');
    });
    
    cancelButton.addEventListener('click', () => {
        newMemberForm.classList.add('hidden');
    });
    
    // Drag and drop functionality
    let draggedMember = null;
    
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
    
    document.querySelectorAll('.family-member').forEach(member => {
        setupDragEvents(member);
    });
    
    deleteZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('active');
    });
    
    deleteZone.addEventListener('dragleave', function() {
        this.classList.remove('active');
    });
    
    deleteZone.addEventListener('drop', function(e) {
        e.preventDefault();
        if (draggedMember) {
            draggedMember.remove();
            // Here you would make an API call to delete from backend
        }
        this.classList.remove('active');
        this.classList.add('hidden');
    });
    
    // Edit member functionality
    function setupEditButton(button) {
        button.addEventListener('click', function() {
            const memberCard = this.closest('.family-member');
            const name = memberCard.querySelector('h3').textContent;
            // Here you would show an edit form with the member's current details
            alert(`Editing: ${name}`);
        });
    }
    
    document.querySelectorAll('.edit-member').forEach(button => {
        setupEditButton(button);
    });
    
    // Form submission for new member
    addMemberForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const firstName = this.querySelector('input[type="text"]:nth-of-type(1)').value;
        const lastName = this.querySelector('input[type="text"]:nth-of-type(2)').value;
        const email = this.querySelector('input[type="email"]').value;
        
        if (firstName && lastName) {
            // Create new member card
            const initials = `${firstName.charAt(0)}${lastName.charAt(0)}`;
            const newMember = document.createElement('div');
            newMember.className = 'family-member relative bg-gray-50 p-4 rounded-xl flex items-center justify-between cursor-move';
            newMember.setAttribute('draggable', 'true');
            newMember.innerHTML = `
                <div class="flex items-center space-x-4">
                    <div class="w-12 h-12 rounded-full bg-gray-300 flex items-center justify-center text-gray-600">
                        <span class="text-lg font-medium">${initials}</span>
                    </div>
                    <div>
                        <h3 class="font-medium text-gray-800">${firstName} ${lastName}</h3>
                        <p class="text-sm text-gray-500">Shared access</p>
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
            
            // Add drag events to new member
            setupDragEvents(newMember);
            
            // Add edit event
            setupEditButton(newMember.querySelector('.edit-member'));
            
            membersContainer.appendChild(newMember);
            this.reset();
            newMemberForm.classList.add('hidden');
            
            // Here you would make an API call to save the new member
        }
    });
});