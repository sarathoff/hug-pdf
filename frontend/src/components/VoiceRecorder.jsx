import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const VoiceRecorder = ({ onTranscriptComplete, onClose }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);

  // Start recording
  const startRecording = async () => {
    try {
      setError(null);
      setTranscript('');
      
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Set up audio level visualization
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;
      
      // Start visualizing audio levels
      visualizeAudioLevel();
      
      // Set up MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        // Stop audio level visualization
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
        
        // Close AudioContext safely
        if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
          try {
            await audioContextRef.current.close();
          } catch (err) {
            console.warn('Error closing AudioContext:', err);
          }
          audioContextRef.current = null;
        }
        
        // Create audio blob and send to backend
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      console.error('Error starting recording:', err);
      if (err.name === 'NotAllowedError') {
        setError('Microphone access denied. Please allow microphone access and try again.');
      } else {
        setError('Failed to start recording. Please check your microphone.');
      }
    }
  };

  // Visualize audio level
  const visualizeAudioLevel = () => {
    if (!analyserRef.current) return;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const updateLevel = () => {
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(Math.min(100, (average / 255) * 100));
      animationFrameRef.current = requestAnimationFrame(updateLevel);
    };
    
    updateLevel();
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // Transcribe audio using backend API
  const transcribeAudio = async (audioBlob) => {
    setIsTranscribing(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('language', 'auto'); // Auto-detect language
      
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.post(
        `${BACKEND_URL}/api/transcribe-audio`,
        formData,
        { headers }
      );
      
      if (response.data.success) {
        setTranscript(response.data.text);
        // Call parent callback with transcript
        if (onTranscriptComplete) {
          onTranscriptComplete(response.data.text);
        }
      } else {
        setError(response.data.error || 'Transcription failed');
      }
    } catch (err) {
      console.error('Transcription error:', err);
      if (err.response?.status === 500 && err.response?.data?.detail?.includes('API key not configured')) {
        setError('Speech-to-Text API is not configured. Please contact support.');
      } else {
        setError(err.response?.data?.detail || 'Failed to transcribe audio. Please try again.');
      }
    } finally {
      setIsTranscribing(false);
      setRecordingTime(0);
    }
  };

  // Format time as MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(err => {
          console.warn('Error closing AudioContext on unmount:', err);
        });
      }
    };
  }, []);

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-in fade-in duration-200">
      <Card className="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        <CardContent className="p-6">
          <div className="text-center space-y-6">
            {/* Header */}
            <div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Voice Input</h3>
              <p className="text-sm text-slate-600">
                {isRecording ? 'Recording your voice...' : isTranscribing ? 'Transcribing...' : 'Click to start recording'}
              </p>
            </div>

            {/* Recording Visualization */}
            <div className="relative">
              <div className={`w-32 h-32 mx-auto rounded-full flex items-center justify-center transition-all duration-300 ${
                isRecording ? 'bg-red-100 animate-pulse' : 'bg-violet-100'
              }`}>
                {isTranscribing ? (
                  <Loader2 className="w-16 h-16 text-violet-600 animate-spin" />
                ) : (
                  <Mic className={`w-16 h-16 ${isRecording ? 'text-red-600' : 'text-violet-600'}`} />
                )}
              </div>
              
              {/* Audio level indicator */}
              {isRecording && (
                <div className="mt-4">
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-red-500 transition-all duration-100"
                      style={{ width: `${audioLevel}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Timer */}
            {isRecording && (
              <div className="text-3xl font-mono font-bold text-slate-900">
                {formatTime(recordingTime)}
              </div>
            )}

            {/* Transcript Display */}
            {transcript && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-left">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-green-900 mb-1">Transcription Complete</p>
                    <p className="text-sm text-slate-700">{transcript}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-left">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-900">{error}</p>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              {!isRecording && !isTranscribing && !transcript && (
                <>
                  <Button
                    onClick={startRecording}
                    className="flex-1 bg-violet-600 hover:bg-violet-700 text-white"
                  >
                    <Mic className="w-4 h-4 mr-2" />
                    Start Recording
                  </Button>
                  <Button
                    onClick={onClose}
                    variant="outline"
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </>
              )}
              
              {isRecording && (
                <Button
                  onClick={stopRecording}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  <Square className="w-4 h-4 mr-2" />
                  Stop Recording
                </Button>
              )}
              
              {(transcript || error) && !isTranscribing && (
                <>
                  {transcript && (
                    <Button
                      onClick={onClose}
                      className="flex-1 bg-violet-600 hover:bg-violet-700 text-white"
                    >
                      Use This Text
                    </Button>
                  )}
                  <Button
                    onClick={() => {
                      setTranscript('');
                      setError(null);
                      setRecordingTime(0);
                    }}
                    variant="outline"
                    className="flex-1"
                  >
                    Try Again
                  </Button>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VoiceRecorder;
