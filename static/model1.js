// Updated symptoms array
const symptoms = ["itching", "skin_rash", " continuous_sneezing", " shivering", " stomach_pain", " acidity", " vomiting", " indigestion", " muscle_wasting", " patches_in_throat", " fatigue", " weight_loss", " sunken_eyes", " cough", " headache", " chest_pain", " back_pain", " weakness_in_limbs", " chills", " joint_pain", " yellowish_skin", " constipation", " pain_during_bowel_movements", " breathlessness", " cramps", " weight_gain", " mood_swings", " neck_pain", " muscle_weakness", " stiff_neck", " pus_filled_pimples", " burning_micturition", " bladder_discomfort", " high_fever", " nodal_skin_eruptions", " ulcers_on_tongue", " loss_of_appetite", " restlessness", " dehydration", " dizziness", " weakness_of_one_body_side", " lethargy", " nausea", " abdominal_pain", " pain_in_anal_region", " sweating", " bruising", " cold_hands_and_feets", " anxiety", " knee_pain", " swelling_joints", " blackheads", " foul_smell_of urine", " skin_peeling", " blister", " dischromic _patches", " watering_from_eyes", " extra_marital_contacts", " diarrhoea", " loss_of_balance", " blurred_and_distorted_vision", " altered_sensorium", " dark_urine", " swelling_of_stomach", " bloody_stool", " obesity", " hip_joint_pain", " movement_stiffness", " spinning_movements", " scurring", " continuous_feel_of_urine", " silver_like_dusting", " red_sore_around_nose", nan, " spotting_ urination", " passage_of_gases", " irregular_sugar_level", " family_history", " lack_of_concentration", " excessive_hunger", " yellowing_of_eyes", " distention_of_abdomen", " irritation_in_anus", " swollen_legs", " painful_walking", " small_dents_in_nails", " yellow_crust_ooze", " internal_itching", " mucoid_sputum", " history_of_alcohol_consumption", " swollen_blood_vessels", " unsteadiness", " inflammatory_nails", " depression", " fluid_overload", " swelled_lymph_nodes", " malaise", " prominent_veins_on_calf", " puffy_face_and_eyes", " fast_heart_rate", " irritability", " muscle_pain", " mild_fever", " yellow_urine", " phlegm", " enlarged_thyroid", " increased_appetite", " visual_disturbances", " brittle_nails", " drying_and_tingling_lips", " polyuria", " pain_behind_the_eyes", " toxic_look_(typhos)", " throat_irritation", " swollen_extremeties", " slurred_speech", " red_spots_over_body", " belly_pain", " receiving_blood_transfusion", " acute_liver_failure", " redness_of_eyes", " rusty_sputum", " abnormal_menstruation", " receiving_unsterile_injections", " coma", " sinus_pressure", " palpitations", " stomach_bleeding", " runny_nose", " congestion", " blood_in_sputum", " loss_of_smell"];
function showSuggestions(inputElement) {
    const suggestionBox = inputElement.nextElementSibling;
    suggestionBox.innerHTML = '';

    if (inputElement.value) {
        const filteredSuggestions = symptoms.filter(suggestion => 
            suggestion.toLowerCase().includes(inputElement.value.toLowerCase())
        );

        if (filteredSuggestions.length > 0) {
            suggestionBox.style.display = 'block';
            filteredSuggestions.forEach(suggestion => {
                const suggestionItem = document.createElement('div');
                suggestionItem.textContent = suggestion;
                suggestionItem.classList.add('suggestion-item');
                suggestionItem.onclick = () => {
                    inputElement.value = suggestion;
                    suggestionBox.style.display = 'none';
                };
                suggestionBox.appendChild(suggestionItem);
            });
        } else {
            suggestionBox.style.display = 'none';
        }
    } else {
        suggestionBox.style.display = 'none';
    }
}

// Add event listeners to all symptom input fields
document.addEventListener('DOMContentLoaded', function() {
    const symptomInputs = document.querySelectorAll('input[id^="symptom"]');
    symptomInputs.forEach(input => {
        input.addEventListener('input', () => showSuggestions(input));
    });

    // Close suggestion box when clicking outside
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.input-group')) {
            const suggestionBoxes = document.querySelectorAll('.suggestions');
            suggestionBoxes.forEach(box => box.style.display = 'none');
        }
    });

// Global variable to keep track of the current set
let currentSet = 0;

function loadMoreSymptoms() {
    console.log("loadMoreSymptoms function called");
    // const sets = [
    //     document.getElementById('additional-symptoms-1'),
    //     document.getElementById('additional-symptoms-2'),
    //     document.getElementById('additional-symptoms-3'),
    //     document.getElementById('additional-symptoms-4')
    // ];

    // console.log("Current set:", currentSet);
    // console.log("Sets:", sets);

    // if (sets[currentSet]) {
    //     console.log("Showing set:", currentSet);
    //     sets[currentSet].style.display = 'flex';
    //     currentSet++;
    // } else {
    //     console.log("No more sets to show");
    // }

    // if (currentSet === sets.length) {
    //     const loadMoreButton = document.querySelector('.load-more');
    //     if (loadMoreButton) {
    //         console.log("Hiding load more button");
    //         loadMoreButton.style.display = 'none';
    //     } else {
    //         console.log("Load more button not found");
    //     }
    // }
}

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



// const option1 = document.querySelector('#symptom');
// function predictedDisease(){
//     console.log(option1)
// }