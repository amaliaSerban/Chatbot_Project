import React, { useState, useEffect } from 'react';
import './App.css';


/*function that displays the text smoothly*/
function TypingMessage({ text }) {
  const [displayed, setDisplayed] = useState('');

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i + 1));
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 20);

    return () => clearInterval(interval);
  }, [text]);

  return <div className="message-bubble assistant">{displayed}</div>;
}

function App() {
  const [patient, setPatient] = useState(null);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loadingFeedback, setLoadingFeedback] = useState(false);

  const loadNewPatient = async () => {
    try {
      const res = await fetch('http://localhost:5000/new-patient');
      const data = await res.json();
      setPatient(data.patient);
      setSystemPrompt(data.prompt);
      setMessages([{ role: 'system', content: data.prompt }]);
      setFeedback('');
    } catch (err) {
      console.error("Failed to fetch new patient:", err);
    }
  };

  useEffect(() => {
    loadNewPatient();
  }, []);

const sendMessage = async () => {
  if (!input.trim()) return;
  const userMessage = { role: 'user', content: input };
  const fullMessages = [...messages, userMessage];
  setMessages(fullMessages);
  setInput('');

  // 🧼 Strip extra keys before sending to backend
  const sanitizedMessages = fullMessages.map(({ role, content }) => ({ role, content }));

  try {
    const res = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: sanitizedMessages })
    });

    const data = await res.json();
    if (data.reply) {
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply, typing: true }]);
    }
  } catch (err) {
    console.error("Chat error:", err);
  }
};

const endConversation = async () => {
  setLoadingFeedback(true);

  // 🧼 Strip extra keys before sending to backend
  const sanitizedMessages = messages.map(({ role, content }) => ({ role, content }));

  try {
    const res = await fetch('http://localhost:5000/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: sanitizedMessages })
    });

    const data = await res.json();
    if (data.feedback) {
      setFeedback(data.feedback);
    } else {
      setFeedback("⚠️ No feedback received.");
    }
  } catch (err) {
    console.error("Feedback error:", err);
    setFeedback("Error fetching feedback.");
  }

  setLoadingFeedback(false);
};

  return (
    <div className="App">
      <div className="sidebar">
        <h2>Patient Information</h2>
        <hr />
        {patient && (
          <ul>
            <li><strong>Full Name:</strong> {patient.First_Name} {patient.Last_Name}</li>
            <li><strong>Patient ID:</strong> {patient.Patient_ID}</li>
            <li><strong>Age:</strong> {patient.Age} years</li>
            <li><strong>Gender:</strong> {patient.Gender}</li>
            <li><strong>Birthdate:</strong> {patient.Birthdate}</li>
            <li><strong>Procedure:</strong> {patient.Procedure}</li>
            <li><strong>Condition:</strong> {patient.Condition}</li>
            <li><strong>Contrast Used:</strong> {patient.Contrast ? 'Yes' : 'No'}</li>
            <li><strong>Length of stay:</strong> {patient.Length_of_Stay} days</li>
            <li><strong>Readmission:</strong> {patient.Readmission}</li>
            <li><strong>Outcome:</strong> {patient.Outcome}</li>
            <li><strong>Satisfaction:</strong> {patient.Satisfaction}/5</li>
          </ul>
        )}
        <button onClick={loadNewPatient}>🔄 Reset Simulation</button>
      </div>

      <div className="chat-panel">
        <div className="chat-header">EmpathAI (pre alpha 0.3)</div>
        <div className="chat-box">
          {messages.filter(msg => msg.role !== 'system').map((msg, index) => (
            <div key={index} className={`message-wrapper ${msg.role}`}>
              <div className="avatar">{msg.role === 'user' ? '🧑‍⚕️' : '🤒'}</div>
              {msg.role === 'assistant' && msg.typing ? (
                <TypingMessage text={msg.content} />
              ) : (
                <div className={`message-bubble ${msg.role}`}>{msg.content}</div>
              )}
            </div>
          ))}
        </div>

        <div className="input-row">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Type your response..."
            disabled={!!feedback}
          />
          <button onClick={sendMessage} className="send-btn" disabled={!!feedback}>
            Send
          </button>
        </div>

        <div style={{ marginTop: '1rem' }}>
          <button onClick={endConversation} className="send-btn" disabled={!!feedback}>
            Get Feedback
          </button>
        </div>

        {loadingFeedback && <p>Generating feedback...</p>}

        {feedback && (
          <div className="feedback-box">
            <h3>Feedback</h3>
            {feedback}
            <div style={{ marginTop: '1rem' }}>
              <button onClick={loadNewPatient} className="send-btn">
                🔄 Restart with New Patient
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
