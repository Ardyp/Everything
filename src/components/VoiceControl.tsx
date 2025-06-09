import { useState, useEffect, useRef } from 'react';
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/solid';
import { API_URL, WS_URL } from '../config';

interface VoiceControlProps {
  onCommand: (command: string) => void;
}

export default function VoiceControl({ onCommand }: VoiceControlProps) {
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState('');
  const [wakeWord, setWakeWord] = useState('agent');
  const [alwaysOn, setAlwaysOn] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const connectWebSocket = () => {
      const ws = new WebSocket(`${WS_URL}/voice/ws`);

      ws.onopen = () => {
        setStatus('Connected to voice service');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action) {
          onCommand(data.action);
        }
      };

      ws.onerror = (error) => {
        setStatus('Error connecting to voice service');
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        setStatus('Disconnected from voice service');
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 5000);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [onCommand]);

  const toggleListening = async () => {
    setIsListening(!isListening);
    
    if (!isListening) {
      setStatus('Listening...');
    } else {
      setStatus('Stopped listening');
    }
  };

  const updateWakeWord = async () => {
    try {
      const response = await fetch(`${API_URL}/voice/wake-word`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ wake_word: wakeWord }),
      });

      if (!response.ok) {
        throw new Error('Failed to update wake word');
      }

      setStatus(`Wake word updated to: ${wakeWord}`);
    } catch (error) {
      console.error('Error updating wake word:', error);
      setStatus('Error updating wake word');
    }
  };

  return (
    <div className="fixed bottom-4 right-4 flex flex-col items-end space-y-4">
      {/* Settings panel */}
      <div className="bg-white rounded-lg shadow-lg p-4 w-64">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Wake Word</label>
          <div className="mt-1 flex rounded-md shadow-sm">
            <input
              type="text"
              value={wakeWord}
              onChange={(e) => setWakeWord(e.target.value)}
              className="flex-1 rounded-l-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <button
              onClick={updateWakeWord}
              className="relative -ml-px inline-flex items-center rounded-r-md border border-gray-300 bg-gray-50 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              Update
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={alwaysOn}
              onChange={(e) => setAlwaysOn(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-900">Always On</span>
          </label>
        </div>

        <div className="mt-2 text-sm text-gray-500">
          {status}
        </div>
      </div>

      {/* Microphone button */}
      <button
        onClick={toggleListening}
        className={`rounded-full p-4 shadow-lg ${
          isListening
            ? 'bg-red-500 hover:bg-red-600'
            : 'bg-indigo-500 hover:bg-indigo-600'
        }`}
      >
        {isListening ? (
          <StopIcon className="h-6 w-6 text-white" />
        ) : (
          <MicrophoneIcon className="h-6 w-6 text-white" />
        )}
      </button>
    </div>
  );
} 