// swampgpt.js

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('autocomplete-input');
    const selectedOptionsList = document.getElementById('selected-options-list');
    const suggestionsList = document.getElementById('suggestions-list');
    const getRecommendationButton = document.getElementById('get-recommendation-button');
    const selectedOptions = [];
    const loaderContainer = document.getElementById('loader-container');
    let buttonClicked = false; // Keeps track of whether the GetReco button has been clicked
    let selectedFormat = 'Any'; // Default value

    function showLoader() {
        loaderContainer.style.display = 'flex';
    }

    function hideLoader() {
        loaderContainer.style.display = 'none';
    }

    input.addEventListener('input', function () {
        const query = input.value.trim();
        if (query) {
            fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsList.innerHTML = '';
                    data.slice(0, 4).forEach(suggestion => { // Limit the suggestions to 5
                        const li = document.createElement('li');
                        li.textContent = suggestion;
                        li.style.cursor = 'pointer';
                        li.addEventListener('click', function () {
                            addSelectedOption(suggestion);
                            input.value = '';
                            suggestionsList.innerHTML = '';
                        });
                        suggestionsList.appendChild(li);
                    });
                });
        } else {
            suggestionsList.innerHTML = '';
        }
        // New code for disabling button and showing warning
        if (selectedOptions.length < 3 || selectedOptions.length > 10) {
            getRecommendationButton.disabled = true;
            getRecommendationButton.classList.add('disabled');
            getRecommendationButton.setAttribute('title', 'Please select between 3 and 10 cards for recommendations.');
        } else {
            getRecommendationButton.disabled = false;
            getRecommendationButton.classList.remove('disabled');
            getRecommendationButton.removeAttribute('title');
        }
    });

    function addSelectedOption(option) {
        if (!selectedOptions.includes(option)) {
            selectedOptions.push(option);
            renderSelectedOptions();
            resetButtonState(); // Reset the GetReco button
        }
    }

    function removeSelectedOption(option) {
        const index = selectedOptions.indexOf(option);
        if (index !== -1) {
            selectedOptions.splice(index, 1);
            renderSelectedOptions();
            resetButtonState(); // Reset the GetReco button
        }
    }

    function resetButtonState() {
        buttonClicked = false; // Reset the buttonClicked flag
        getRecommendationButton.disabled = false; // Re-enable the getreco button
        getRecommendationButton.classList.remove('disabled'); // Remove the disabled class to give a visual cue to the user
    }

    function renderSelectedOptions() {
        selectedOptionsList.innerHTML = '';
        selectedOptions.forEach(option => {
            const li = document.createElement('li');
            li.textContent = option;
            li.style.margin = '5px';
            li.style.padding = '5px';
            li.style.backgroundColor = 'lightgray';
            li.style.color = 'black'; // Set font color to black
            li.style.borderRadius = '5px';
            li.style.cursor = 'pointer';
            li.addEventListener('click', function () {
                removeSelectedOption(option);
            });
            selectedOptionsList.appendChild(li);
        });
    }

    getRecommendationButton.addEventListener('click', function () {
        if (!buttonClicked && selectedOptions.length >= 3 && selectedOptions.length <= 10) {
            buttonClicked = true;
            getRecommendationButton.disabled = true;
            getRecommendationButton.classList.add('disabled');
            showLoader();
    
            fetch('/send_gpt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ selectedOptions, selectedFormat }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok.');
                }
                return response.json();
            })
            .then(data => {
                   
                // Display Start Section
                const startContainer = document.getElementById('start-section');
                startContainer.textContent = data.start_section;

    
                // Clear the recommendations and images container
                const recommendationsList = document.getElementById('recommendations-list');
                const imagesContainer = document.getElementById('card-images');
                
                while (recommendationsList.firstChild) {
                    recommendationsList.removeChild(recommendationsList.firstChild);
                }
                
                while (imagesContainer.firstChild) {
                    imagesContainer.removeChild(imagesContainer.firstChild);
                }
                
                // Check the data structure
                console.log('Data received from server:', data);

                // Create a list of recommendations
                data.response_with_images.forEach(item => {
                    // Create a recommendation item
                    const recommendationItem = document.createElement('div');
                    recommendationItem.classList.add('recommendation-item');

                // Create an image element
                const img = document.createElement('img');
                img.src = item.image_url[0]; // Assuming image_url is an array
                img.alt = item.card_name;
                img.classList.add('recommendation-card');
                
                // Create a text element for the recommendation
                const recommendationText = document.createElement('div');
                recommendationText.classList.add('recommendation-text');
                recommendationText.innerHTML = item.recommendation;

                // Append the image and text to the recommendation item
                recommendationItem.appendChild(img);
                recommendationItem.appendChild(recommendationText);

                // Append the recommendation item to the recommendations list
                recommendationsList.appendChild(recommendationItem);
        });
                // Update outro section
                const outroSection = document.getElementById('outro-section');
                outroSection.innerHTML = data.outro_section; // Add outro content

                // Update start section if needed
                const startSection = document.getElementById('start-section');
                startSection.innerHTML = data.start_section; // Add start content
})
            .catch(error => {
                console.error('Error fetching recommendations:', error);
                // Handle errors here
            })
            .finally(() => {
                hideLoader();
                getRecommendationButton.disabled = false;
            });
        } else {
            alert('Please select between 3 and 10 cards for recommendations.'); // Show an alert for invalid selection
        }
    });
    
        // Get references to elements
    const formatSelect = document.getElementById('format-select');

    // Add event listener to the dropdown menu
    formatSelect.addEventListener('change', function () {
        // Get the selected value
        selectedFormat = this.value;

        // Log the selected format
        console.log('Selected format:', selectedFormat);

    
    });

});
