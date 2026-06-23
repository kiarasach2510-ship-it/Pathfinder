//This is the starter code for js
async function getAdvice() {
    const interests = document.getElementById("interests").value;
    const goals = document.getElementById("goals").value;
    const result = document.getElementById("result");

    result.innerHTML = "Finding your path...";

    const response = await fetch("http://127.0.0.1:5000/career-advice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interests, goals })
    });

    const data = await response.json();
    result.innerHTML = "<h2>Your Results:</h2><p>" + data.advice.replace(/\n/g, "<br>") + "</p>";
}