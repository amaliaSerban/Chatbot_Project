import React, { useState, useEffect } from 'react';

function App() {
  const [patient, setPatient] = useState(null);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Load new patient info and prompt
  const loadNewPatient = async () => {
    try {
      const res = await fetch('http://localhost:5000/new-patient');
      const data = await res.json();
      setPatient(data.patient);
      setSystemPrompt(data.prompt);
      setMessages([{ role: 'system', content: data.prompt }]);  // Reset with fresh prompt
    } catch (err) {
      console.error("Failed to fetch new patient:", err);
    }
  };

  // Fetch patient on first load
  useEffect(() => {
    loadNewPatient();
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const fullMessages = [...messages, userMessage];

    setMessages(fullMessages);
    setInput('');

    try {
      const res = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: fullMessages })
      });

      const data = await res.json();
      if (data.reply) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      }
    } catch (err) {
      console.error("❌ Chat error:", err);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '700px', margin: 'auto' }}>
      <h1>EmpathAI</h1>

      <button onClick={loadNewPatient} style={{ marginBottom: '1rem' }}>
        🔄 Load New Patient
      </button>

      {patient && (
        <div style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ccc' }}>
          <h3>👤 Patient Details</h3>
          <ul>
            <li><strong>Age:</strong> {patient.Age}</li>
            <li><strong>Gender:</strong> {patient.Gender}</li>
            <li><strong>Condition:</strong> {patient.Condition}</li>
            <li><strong>Procedure:</strong> {patient.Procedure}</li>
            <li><strong>Length of Stay:</strong> {patient.Length_of_Stay} days</li>
            <li><strong>Readmission:</strong> {patient.Readmission}</li>
            <li><strong>Satisfaction:</strong> {patient.Satisfaction}/5</li>
          </ul>
        </div>
      )}

      <div style={{ minHeight: '300px', padding: '1rem', border: '1px solid #eee', background: '#f9f9f9' }}>
        {messages.filter(msg => msg.role !== 'system').map((msg, index) => (
          <div key={index}>
            <strong>{msg.role === 'user' ? 'Nurse' : 'Patient'}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && sendMessage()}
        placeholder="Ask the patient something..."
        style={{ width: '75%', padding: '0.5rem' }}
      />
      <button onClick={sendMessage} style={{ padding: '0.5rem', marginLeft: '0.5rem' }}>Send</button>
    </div>
  );
}

export default App;
