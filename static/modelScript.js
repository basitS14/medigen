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

