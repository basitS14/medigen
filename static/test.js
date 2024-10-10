document.addEventListener('DOMContentLoaded', function() {
    let clickCount = 0;
    const button = document.getElementById('loadMoreButton');
    const content = document.getElementById('content');

    button.addEventListener('click', function() {
        clickCount++;
        const newParagraph = document.createElement('p');
        newParagraph.textContent = `New content ${clickCount}`;
        content.appendChild(newParagraph);
        console.log('Button clicked, content added');
    });

    console.log('JavaScript loaded');
});