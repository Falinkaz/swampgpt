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
                    data.slice(0, 4).forEach(suggestion => { // Limit the suggestions to 4
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
                // Clear the images container
                const imagesContainer = document.getElementById('card-images');
                while (imagesContainer.firstChild) {
                    imagesContainer.removeChild(imagesContainer.firstChild);
                }
            
                // Check the data structure
                console.log('Data received from server:', data);
            
                // Iterate over the data and create HTML elements
                data.response_with_images.forEach(item => {
                    const recommendationItem = document.createElement('div');
                    recommendationItem.classList.add('recommendation-item');
            
                    const img = document.createElement('img');
                    img.src = item.image_url;
                    img.alt = "Card image";
                    img.classList.add('recommendation-card');
            
                    const recommendationText = document.createElement('div');
                    recommendationText.classList.add('recommendation-text');
                    recommendationText.innerHTML = item.recommendation;
            
                    recommendationItem.appendChild(img);
                    recommendationItem.appendChild(recommendationText);
            
                    imagesContainer.appendChild(recommendationItem);
                });
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

    document.querySelectorAll('.format').forEach(format => {
        format.addEventListener('click', function () {
            // Remove the 'highlighted' class from all formats
            document.querySelectorAll('.format').forEach(f => {
                f.classList.remove('highlighted');
            });

            // Add the 'highlighted' class to the clicked format
            this.classList.add('highlighted');

            // Capture the selected format
            selectedFormat = this.textContent;
        });
    });
});
