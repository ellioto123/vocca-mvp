import { useState } from 'react';
import DailyIframe from '@daily-co/daily-js';

function App() {
  const [transcript, setTranscript] = useState('');
  const [isActive, setIsActive] = useState(false);
  const [callFrame, setCallFrame] = useState(null);

  const startConversation = async () => {
    console.log("Starting conversation...");
    setIsActive(true);

    try {
      const res = await fetch('http://localhost:7860/connect', { method: 'POST' });
      const data = await res.json();
      console.log("Received from backend:", data);

      const frame = DailyIframe.createFrame({
        iframeStyle: {
          position: 'fixed',
          top: '10%',
          left: '10%',
          width: '80%',
          height: '80%',
          border: '1px solid #ccc',
          borderRadius: '8px',
          zIndex: 1000
        },
        showLeaveButton: true,
      });

      setCallFrame(frame);

      await frame.join({ url: data.room_url, token: data.token });
    } catch (error) {
      console.error("Error connecting to Daily call:", error);
      setIsActive(false);
    }
  };

  const stopConversation = () => {
    console.log("Stopping conversation...");
    if (callFrame) {
      callFrame.leave();
      callFrame.destroy();
      setCallFrame(null);
    }
    setIsActive(false);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f8f9fa'
    }}>
      <h1>Vocca Assistant</h1>

      <button
        onClick={isActive ? stopConversation : startConversation}
        style={{
          padding: '1rem 2rem',
          fontSize: '1.2rem',
          backgroundColor: isActive ? '#dc3545' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          transition: 'background-color 0.3s'
        }}
      >
        {isActive ? 'Stop' : 'Start'} Conversation
      </button>

      <h2 style={{ marginTop: '2rem' }}>Transcription</h2>
      <div
        style={{
          border: '1px solid #ccc',
          padding: '1rem',
          minHeight: '150px',
          width: '80%',
          maxWidth: '600px',
          backgroundColor: 'white',
          borderRadius: '8px',
        }}
      >
        {transcript || '(no transcript yet)'}
      </div>
    </div>
  );
}

export default App;
