// Updated symptoms array
// let symptoms = [];
let currentSet = 0;

function loadMoreSymptoms() {
    console.log("loadMoreSymptoms function called");
    const sets = [
        document.getElementById('additional-symptoms-1'),
        document.getElementById('additional-symptoms-2'),
        document.getElementById('additional-symptoms-3'),
        document.getElementById('additional-symptoms-4')
    ];

    console.log("Current set:", currentSet);
    console.log("Sets:", sets);

    if (sets[currentSet]) {
        console.log("Showing set:", currentSet);
        sets[currentSet].style.display = 'flex';
        currentSet++;
    } else {
        console.log("No more sets to show");
    }

    if (currentSet === sets.length) {
        const loadMoreButton = document.querySelector('.load-more');
        if (loadMoreButton) {
            console.log("Hiding load more button");
            loadMoreButton.style.display = 'none';
        } else {
            console.log("Load more button not found");
        }
    }
}

const option1 = document.querySelector('#symptom');
function predictedDisease(){
    console.log(option1)
}

  



function showSuggestions() {
    console.log("hello")
  
}

// Add event listeners to all symptom input fields
document.addEventListener('load', function() {
    

// Global variable to keep track of the current set

    function textRun() {
        console.log("hii")
    }
    // Add this to ensure the function is called when the button is clicked
    document.addEventListener('DOMContentLoaded', function() {
        const loadMoreButton = document.querySelector('.load-more');
        if (loadMoreButton) {
            loadMoreButton.addEventListener('click', loadMoreSymptoms);
            console.log("Event listener added to load more button");
        } else {
            console.log("Load more button not found on page load");
        }
    });
});

// Keep track of selected symptoms
let selectedSymptoms = new Set();

// Function to check for duplicates and show warning
function handleSymptomSelection(event) {
    const select = event.target;
    const selectedValue = select.value;
    
    // If nothing is selected, just return
    if (!selectedValue) return;
    
    // Check if symptom was already selected
    if (selectedSymptoms.has(selectedValue)) {
        // Reset the select to empty option
        select.value = '';
        
        // Create warning message if it doesn't exist
        let warningMsg = document.getElementById('warning-message');
        if (!warningMsg) {
            warningMsg = document.createElement('div');
            warningMsg.id = 'warning-message';
            warningMsg.style.cssText = `
                color: #dc3545;
                background-color: #ffe6e6;
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
                border: 1px solid #dc3545;
                display: none;
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(warningMsg);
        }
        
        // Show warning message
        warningMsg.textContent = `"${selectedValue.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}" is already selected. Please choose a different symptom.`;
        warningMsg.style.display = 'block';
        
        // Hide warning message after 3 seconds
        setTimeout(() => {
            warningMsg.style.display = 'none';
        }, 3000);
        
        return;
    }
    
    // Remove previous selection for this dropdown if it exists
    const previousValue = select.dataset.previousValue;
    if (previousValue) {
        selectedSymptoms.delete(previousValue);
    }
    
    // Add new selection
    selectedSymptoms.add(selectedValue);
    select.dataset.previousValue = selectedValue;
}

// Add event listeners to all symptom select elements
document.addEventListener('DOMContentLoaded', () => {
    const symptomSelects = document.querySelectorAll('.symptom-select');
    symptomSelects.forEach(select => {
        select.addEventListener('change', handleSymptomSelection);
    });
});

// Clear warning message when clicking outside
document.addEventListener('click', (event) => {
    const warningMsg = document.getElementById('warning-message');
    if (warningMsg && !event.target.classList.contains('symptom-select')) {
        warningMsg.style.display = 'none';
    }
});