// frontend/script.js

const BASE_URL = "http://localhost:8000";

const createStudentBtn = document.getElementById("createStudentBtn");
const studentNameInput = document.getElementById("studentName");
const existingStudentId = document.getElementById("existingStudentId");
const textInput = document.getElementById("textInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const outputDiv = document.getElementById("output");
const feedbackDiv = document.getElementById("feedback");

let currentStudentId = null;

// Create new student
createStudentBtn.addEventListener("click", async () => {
  const name = studentNameInput.value.trim();
  if (!name) {
    alert("Please enter a student name.");
    return;
  }

  try {
    // Send JSON body { "name": "Alice" }
    const resp = await fetch(`${BASE_URL}/students`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name })
    });

    if (!resp.ok) {
      const errData = await resp.json();
      alert("Error creating student: " + (errData.detail || resp.status));
      return;
    }

    const data = await resp.json();
    currentStudentId = data.student_id;
    alert(`Student created: ID = ${currentStudentId}, name = ${data.name}`);
  } catch (err) {
    console.error(err);
    alert("Failed to create student.");
  }
});

// Analyze text
analyzeBtn.addEventListener("click", async () => {
  const text = textInput.value.trim();
  if (!text) {
    alert("Please enter some text.");
    return;
  }

  // Determine which student ID to use
  if (existingStudentId.value) {
    currentStudentId = parseInt(existingStudentId.value, 10);
  }

  if (!currentStudentId) {
    alert("No valid student ID. Please create a student or enter an existing ID.");
    return;
  }

  try {
    // Send JSON body { "student_id": 1, "text": "She go to store..." }
    const resp = await fetch(`${BASE_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        student_id: currentStudentId,
        text
      })
    });

    if (!resp.ok) {
      const errData = await resp.json();
      alert("Error analyzing text: " + (errData.detail || resp.status));
      return;
    }

    const data = await resp.json();
    const { original_text, corrected_text, errors } = data;

    // Display corrected text & annotated errors
    outputDiv.innerHTML = `
      <h3>Corrected Text:</h3>
      <p>${corrected_text}</p>
      <h4>Detected Errors:</h4>
      ${errors.map(err => `
        <div>
          <span class="error-span">${err.original_span}</span>
          <span> → </span>
          <span class="corrected-span">${err.corrected_span}</span>
          <strong>(${err.error_type})</strong>
        </div>
      `).join("")}
    `;

    // Retrieve feedback
    const feedbackResp = await fetch(`${BASE_URL}/students/${currentStudentId}/feedback`);
    if (!feedbackResp.ok) {
      console.log("Could not fetch feedback for user.");
    } else {
      const feedbackData = await feedbackResp.json();
      feedbackDiv.innerHTML = `<strong>Feedback:</strong><br/>${feedbackData.feedback.replace(/\n/g, "<br/>")}`;
    }

  } catch (err) {
    console.error(err);
    alert("Failed to analyze text.");
  }
});
