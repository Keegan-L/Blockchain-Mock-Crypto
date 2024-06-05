import React, { useState, useEffect } from 'react';

function App() {
  const [balance, setBalance] = useState(0);
  const [nodeActive, setNodeActive] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchStatusAndBalance = async () => {
      try {
        const statusResponse = await fetch('http://localhost:5000/status', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'DNT': '1',
          },
          credentials: 'include',  // Ensure credentials are included
        });
        if (!statusResponse.ok) {
          throw new Error(`Failed to fetch node status: ${statusResponse.status}`);
        }
        const statusData = await statusResponse.json();

        const balanceResponse = await fetch('http://localhost:5000/balance', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'DNT': '1',
          },
          credentials: 'include',  // Ensure credentials are included
        });
        if (!balanceResponse.ok) {
          throw new Error(`Failed to fetch balance data: ${balanceResponse.status}`);
        }
        const balanceData = await balanceResponse.json();

        setNodeActive(statusData.active);
        setBalance(balanceData.balance);
      } catch (error) {
        console.error('Failed to fetch status or balance:', error);
        setMessage(`Error: ${error.message}`);
      }
    };

    fetchStatusAndBalance();
    const interval = setInterval(fetchStatusAndBalance, 10000);  // Poll every 10 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Blockchain Wallet</h1>
      <p>Node Status: {nodeActive ? 'Connected' : 'Disconnected'}</p>
      <p>Balance: {balance}</p>
      {message && <div>{message}</div>}
    </div>
  );
}

export default App;
