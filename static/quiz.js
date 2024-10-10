document.getElementById('quiz-form').onsubmit = async function(e) {
    e.preventDefault();
    const answer = document.getElementById('answer').value;
    const response = await fetch('/skill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'command': answer
        })
    });
    const data = await response.json();
    document.getElementById('question').innerText = data.text;
    document.getElementById('answer').value = '';
}


